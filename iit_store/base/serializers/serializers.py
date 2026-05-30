from rest_framework import serializers
from django.contrib.auth.models import User
from base.models.profil import Profil


class ProfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profil
        fields = [
            "id", "telephone", "photo", "date_naissance", "genre", "bio",
            "cree_le", "mis_a_jour_le",
        ]
        read_only_fields = ["cree_le", "mis_a_jour_le"]


class UserSerializer(serializers.ModelSerializer):
    profil = ProfilSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "is_staff", "date_joined", "profil",
        ]
        read_only_fields = ["id", "is_staff", "date_joined"]


class UserUpdateSerializer(serializers.ModelSerializer):
    profil = ProfilSerializer(required=False)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "profil"]

    def update(self, instance, validated_data):
        profil_data = validated_data.pop("profil", None)
        # Mise à jour des champs de l'utilisateur
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Mise à jour ou création du profil imbriqué
        if profil_data:
            profil, _ = Profil.objects.get_or_create(user=instance)
            for attr, value in profil_data.items():
                setattr(profil, attr, value)
            profil.save()

        return instance


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer pour l'inscription d'un nouvel utilisateur."""

    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, label="Confirmer le mot de passe")

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "password", "password2",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password2"):
            raise serializers.ValidationError(
                {"password": "Les mots de passe ne correspondent pas."}
            )
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer pour le changement de mot de passe."""

    ancien_mot_de_passe = serializers.CharField(write_only=True)
    nouveau_mot_de_passe = serializers.CharField(write_only=True, min_length=8)
    confirmation = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["nouveau_mot_de_passe"] != attrs["confirmation"]:
            raise serializers.ValidationError(
                {"nouveau_mot_de_passe": "Les mots de passe ne correspondent pas."}
            )
        return attrs
