from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from base.models.profil import Profil
from base.serializers.serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ProfilSerializer,
    ChangePasswordSerializer,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from base.authentications import CookieJWTAuthentication


class CookieTokenObtainPairView(TokenObtainPairView):
    """
    Obtention de tokens JWT stockés de manière sécurisée dans des cookies HTTP-Only.
    """

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access_token = response.data.get("access")
            refresh_token = response.data.get("refresh")

            # Stockage dans des cookies sécurisés HTTP-Only
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=False,  # Mettre à True en HTTPS/prod
                samesite="Lax",
                max_age=3600,  # 1 heure
            )
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=False,
                samesite="Lax",
                max_age=3600 * 24 * 7,  # 7 jours
            )
        return response


class CookieTokenRefreshView(TokenRefreshView):
    """
    Rafraîchissement automatique de tokens JWT via cookies.
    """

    def post(self, request, *args, **kwargs):
        # Si le refresh token n'est pas dans le corps, on le cherche dans les cookies
        if "refresh" not in request.data:
            cookie_refresh = request.COOKIES.get("refresh_token")
            if cookie_refresh:
                request.data["refresh"] = cookie_refresh

        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access_token = response.data.get("access")
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=False,
                samesite="Lax",
                max_age=3600,
            )
        return response


class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD utilisateurs.
    - POST /api/users/ → inscription (public)
    - GET  /api/users/me/ → profil courant (authentifié)
    """

    queryset = User.objects.select_related("profil").all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        if self.action in ["list", "destroy"]:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=["get", "patch"], url_path="me")
    def me(self, request):
        """Retourne ou met à jour le profil de l'utilisateur courant."""
        if request.method == "GET":
            serializer = UserSerializer(request.user, context={"request": request})
            return Response(serializer.data)
        
        # Utiliser le serializer dédié pour la mise à jour (PATCH)
        serializer = UserUpdateSerializer(
            request.user, data=request.data, partial=True,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Récupération fraîche depuis la base de données pour vider les caches mémoire des relations
        fresh_user = User.objects.select_related("profil").get(pk=request.user.pk)
        
        # Retourner la réponse en utilisant UserSerializer pour conserver la structure complète
        response_serializer = UserSerializer(fresh_user, context={"request": request})
        return Response(response_serializer.data)

    @action(detail=False, methods=["post"], url_path="change-password")
    def change_password(self, request):
        """Changement de mot de passe."""
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data["ancien_mot_de_passe"]):
            return Response(
                {"detail": "Mot de passe actuel incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(serializer.validated_data["nouveau_mot_de_passe"])
        user.save()
        return Response({"detail": "Mot de passe mis à jour avec succès."})


class ProfilViewSet(viewsets.ModelViewSet):
    """Gestion des profils utilisateurs."""

    serializer_class = ProfilSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Profil.objects.select_related("user").all()
        return Profil.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
