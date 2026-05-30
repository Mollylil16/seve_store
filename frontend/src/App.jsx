import React, { useState, useEffect } from 'react';
import { ShoppingBag, User, LogOut, ArrowRight, X, Plus, Minus, Search, Sliders, CheckCircle, ShieldCheck, Heart } from 'lucide-react';

const API_URL = 'http://127.0.0.1:8000/api';

export default function App() {
  // App States
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [cart, setCart] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('access_token'));
  
  // Modals & Panels UI
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [isCheckoutOpen, setIsCheckoutOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [authMode, setAuthMode] = useState('login'); // 'login' | 'signup'
  
  // Search & Filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [priceMin, setPriceMin] = useState('');
  const [priceMax, setPriceMax] = useState('');
  const [inStockOnly, setInStockOnly] = useState(false);
  
  // Auth Form Input state
  const [usernameInput, setUsernameInput] = useState('');
  const [passwordInput, setPasswordInput] = useState('');
  const [confirmPasswordInput, setConfirmPasswordInput] = useState('');
  const [emailInput, setEmailInput] = useState('');
  const [firstNameInput, setFirstNameInput] = useState('');
  const [lastNameInput, setLastNameInput] = useState('');
  
  // Profile update input state
  const [phoneInput, setPhoneInput] = useState('');
  const [bioInput, setBioInput] = useState('');
  const [profileMessage, setProfileMessage] = useState('');

  // Checkout address state
  const [addressText, setAddressText] = useState('');
  const [orderSuccessId, setOrderSuccessId] = useState('');
  const [checkoutError, setCheckoutError] = useState('');

  // 1. Core initialization
  useEffect(() => {
    fetchProducts();
    fetchCategories();
    if (token) {
      fetchCurrentUser();
      fetchCart();
    }
  }, [token, selectedCategory, priceMin, priceMax, inStockOnly]);

  // Fetch products with filters
  const fetchProducts = async () => {
    try {
      let queryParams = [];
      if (selectedCategory) queryParams.push(`categorie=${selectedCategory}`);
      if (priceMin) queryParams.push(`prix_min=${priceMin}`);
      if (priceMax) queryParams.push(`prix_max=${priceMax}`);
      if (inStockOnly) queryParams.push(`en_stock=true`);
      
      const res = await fetch(`${API_URL}/produits/?${queryParams.join('&')}`);
      if (res.ok) {
        const data = await res.json();
        setProducts(data.results || data);
      }
    } catch (err) {
      console.error("Error fetching products:", err);
    }
  };

  // Fetch categories
  const fetchCategories = async () => {
    try {
      const res = await fetch(`${API_URL}/categories/`);
      if (res.ok) {
        const data = await res.json();
        setCategories(data.results || data);
      }
    } catch (err) {
      console.error("Error fetching categories:", err);
    }
  };

  // Fetch current authenticated user profile
  const fetchCurrentUser = async () => {
    try {
      const res = await fetch(`${API_URL}/users/me/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setCurrentUser(data);
        if (data.profil) {
          setPhoneInput(data.profil.telephone || '');
          setBioInput(data.profil.bio || '');
        }
      } else {
        // Expired token
        handleLogout();
      }
    } catch (err) {
      console.error("Error fetching user profile:", err);
    }
  };

  // Fetch current user cart (dynamic and updated)
  const fetchCart = async () => {
    try {
      const res = await fetch(`${API_URL}/panier/mon-panier/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setCart(data);
      }
    } catch (err) {
      console.error("Error fetching cart:", err);
    }
  };

  // Login handler
  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_URL}/token/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: usernameInput, password: passwordInput })
      });
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('access_token', data.access);
        setToken(data.access);
        setIsAuthOpen(false);
        // Clear fields
        setUsernameInput('');
        setPasswordInput('');
      } else {
        alert("Identifiants incorrects. Veuillez réessayer.");
      }
    } catch (err) {
      console.error("Error logging in:", err);
    }
  };

  // Signup/Register handler
  const handleSignup = async (e) => {
    e.preventDefault();
    if (passwordInput !== confirmPasswordInput) {
      alert("Les mots de passe ne correspondent pas.");
      return;
    }
    try {
      const res = await fetch(`${API_URL}/users/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: usernameInput,
          email: emailInput,
          password: passwordInput,
          password2: confirmPasswordInput,
          first_name: firstNameInput,
          last_name: lastNameInput
        })
      });
      if (res.ok) {
        alert("Inscription réussie ! Vous pouvez maintenant vous connecter.");
        setAuthMode('login');
      } else {
        const errors = await res.json();
        alert(JSON.stringify(errors));
      }
    } catch (err) {
      console.error("Error signing up:", err);
    }
  };

  // Logout handler
  const handleLogout = () => {
    localStorage.removeItem('access_token');
    setToken(null);
    setCurrentUser(null);
    setCart(null);
    setIsProfileOpen(false);
  };

  // Profile update handler
  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_URL}/users/me/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          first_name: currentUser.first_name,
          last_name: currentUser.last_name,
          email: currentUser.email,
          profil: {
            telephone: phoneInput,
            bio: bioInput
          }
        })
      });
      if (res.ok) {
        const updated = await res.json();
        setCurrentUser(updated);
        setProfileMessage("Profil mis à jour avec succès !");
        setTimeout(() => setProfileMessage(''), 4000);
      }
    } catch (err) {
      console.error("Error updating profile:", err);
    }
  };

  // Cart operations
  const addToCart = async (productId, qty = 1) => {
    if (!token) {
      setIsAuthOpen(true);
      return;
    }
    try {
      const res = await fetch(`${API_URL}/panier/ajouter/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ produit_id: productId, quantite: qty })
      });
      if (res.ok) {
        const updatedCart = await res.json();
        setCart(updatedCart);
        setIsCartOpen(true);
      }
    } catch (err) {
      console.error("Error adding to cart:", err);
    }
  };

  const removeFromCart = async (itemId) => {
    try {
      const res = await fetch(`${API_URL}/panier/retirer/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ item_id: itemId })
      });
      if (res.ok) {
        const updatedCart = await res.json();
        setCart(updatedCart);
      }
    } catch (err) {
      console.error("Error removing from cart:", err);
    }
  };

  const clearCart = async () => {
    try {
      const res = await fetch(`${API_URL}/panier/vider/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.ok) {
        setCart({ ...cart, items: [], total: 0, nombre_articles: 0 });
      }
    } catch (err) {
      console.error("Error clearing cart:", err);
    }
  };

  // Place Order transaction
  const handlePlaceOrder = async (e) => {
    e.preventDefault();
    setCheckoutError('');
    try {
      const res = await fetch(`${API_URL}/commandes/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          adresse_livraison_texte: addressText,
          frais_livraison: 0.00
        })
      });
      if (res.ok) {
        const data = await res.json();
        setOrderSuccessId(data.numero);
        setCart(null);
        setAddressText('');
        setIsCheckoutOpen(false);
      } else {
        const errData = await res.json();
        setCheckoutError(errData.detail || "Une erreur est survenue lors de la validation du stock.");
      }
    } catch (err) {
      console.error("Error placing order:", err);
    }
  };

  // Filter products locally by query string
  const filteredProducts = products.filter(p => 
    p.nom.toLowerCase().includes(searchQuery.toLowerCase()) || 
    (p.description && p.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div>
      {/* 1. HEADER / NAVBAR */}
      <nav className="navbar">
        <a href="/" className="logo">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--primary-green)' }}>
            <path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2z" />
            <path d="M12 22c0-5.5-4.5-10-10-10" />
            <path d="M12 2c0 5.5 4.5 10 10 10" />
            <circle cx="12" cy="12" r="3" fill="var(--primary-green)" opacity="0.15" />
          </svg>
          sève.
        </a>
        
        <ul className="nav-links">
          <li><a href="#boutique">BOUTIQUE</a></li>
          <li><a href="#manifeste">SYSTÈMES</a></li>
          <li><a href="#manifeste">ARCHIVES</a></li>
        </ul>
        
        <div className="navbar-actions">
          {token ? (
            <>
              <button className="btn-outline" onClick={() => setIsProfileOpen(true)}>
                <User size={16} style={{ marginRight: '8px' }} />
                {currentUser ? currentUser.first_name || currentUser.username : "PROFIL"}
              </button>
              <button className="btn-outline" onClick={handleLogout} title="Se déconnecter">
                <LogOut size={16} />
              </button>
            </>
          ) : (
            <button className="btn-outline" onClick={() => { setAuthMode('login'); setIsAuthOpen(true); }}>
              <User size={16} style={{ marginRight: '8px' }} />
              CONNEXION
            </button>
          )}

          <button className="btn-outline" onClick={() => setIsCartOpen(true)}>
            <ShoppingBag size={16} style={{ marginRight: '8px' }} />
            PANIER ({cart ? cart.nombre_articles : 0})
          </button>
        </div>
      </nav>

      {/* 2. HERO SECTION */}
      <header className="hero-container">
        <div className="hero-content">
          <h1 className="hero-title">
            Systèmes <span className="italic-word">Naturels</span>,<br />
            Espaces de <span className="italic-word">Beauté.</span>
          </h1>
          <p className="hero-subtitle">
            Une collection de soins botaniques composée selon des principes de conception systémique. Pureté chimique, rituel humain.
          </p>
          <div>
            <a href="#boutique" className="btn-solid">EXPLORER LA COLLECTION</a>
          </div>
        </div>
        
        <div className="hero-leaf-frame">
          <div 
            className="leaf-shape-mask"
            style={{ backgroundImage: `url('https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&q=80&w=800')` }}
          />
        </div>
      </header>

      {/* 3. STOREFRONT & BOUTIQUE SECTION */}
      <section className="collection-section" id="boutique">
        <div className="collection-header">
          <div>
            <div className="collection-meta">SÉRIE 01 — LES ESSENTIELS</div>
            <h2 className="collection-title">La Chimie Verte</h2>
          </div>
          <div className="collection-aside">Conçu pour le corps et l'esprit.</div>
        </div>

        {/* Filters and Search Bar */}
        <div className="filter-bar">
          <div className="filter-group">
            <Search size={16} style={{ opacity: 0.6 }} />
            <input 
              type="text" 
              placeholder="Rechercher un soin..." 
              className="filter-input"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <div className="filter-group">
            <Sliders size={16} style={{ opacity: 0.6 }} />
            <select 
              className="filter-input"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              <option value="">Toutes catégories</option>
              {categories.map(cat => (
                <option key={cat.id} value={cat.id}>{cat.nom}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <input 
              type="number" 
              placeholder="Min €" 
              className="filter-input"
              style={{ width: '80px' }}
              value={priceMin}
              onChange={(e) => setPriceMin(e.target.value)}
            />
            <span>à</span>
            <input 
              type="number" 
              placeholder="Max €" 
              className="filter-input"
              style={{ width: '80px' }}
              value={priceMax}
              onChange={(e) => setPriceMax(e.target.value)}
            />
          </div>

          <div className="filter-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
              <input 
                type="checkbox" 
                checked={inStockOnly} 
                onChange={(e) => setInStockOnly(e.target.checked)}
              />
              En stock uniquement
            </label>
          </div>
        </div>

        {/* Order success notification */}
        {orderSuccessId && (
          <div style={{ background: '#d1e7dd', color: '#0f5132', padding: '20px', borderRadius: '12px', marginBottom: '40px', display: 'flex', alignItems: 'center', gap: '15px' }}>
            <CheckCircle size={32} />
            <div>
              <h4 style={{ fontWeight: '700' }}>Commande passée avec succès !</h4>
              <p>Votre numéro de commande est : <strong>#{orderSuccessId}</strong>. Notre laboratoire prépare vos soins.</p>
            </div>
            <button className="btn-outline" style={{ marginLeft: 'auto' }} onClick={() => setOrderSuccessId('')}>OK</button>
          </div>
        )}

        {/* Product Cards Grid */}
        <div className="product-grid">
          {filteredProducts.map(p => {
            // Unsplash visuals matching your cosmetic products
            let imgUrl = "https://images.unsplash.com/photo-1607006342411-92fc98c11093?auto=format&fit=crop&q=80&w=600";
            if (p.nom.toLowerCase().includes('huile')) {
              imgUrl = "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&q=80&w=600";
            } else if (p.nom.toLowerCase().includes('baume')) {
              imgUrl = "https://images.unsplash.com/photo-1601049541289-9b1b7bbbfe19?auto=format&fit=crop&q=80&w=600";
            }
            
            // Format beautiful serif words for the card titles
            const splitTitle = p.nom.split(' ');
            const mainName = splitTitle.slice(0, -1).join(' ');
            const italicName = splitTitle.slice(-1)[0] || '';

            return (
              <div className="product-card" key={p.id}>
                <div className="product-image-container">
                  <div className="pentagon-bg"></div>
                  <img src={imgUrl} alt={p.nom} className="product-image" />
                </div>
                
                <div className="product-card-meta">
                  <span>RÉF. {p.id}-A</span>
                  <span>{p.stock > 0 ? `${p.stock} DISPO` : "ÉPUISÉ"}</span>
                </div>

                <div className="product-info">
                  <h3 className="product-card-title">
                    {mainName} <span className="italic-word">{italicName}</span>
                  </h3>
                  <p className="product-card-desc">
                    {p.description_courte || "Une pure formulation botanique aux essences végétales actives pour nourrir et structurer la barrière cutanée."}
                  </p>
                </div>

                <div className="product-card-footer">
                  <div className="product-price">
                    {p.prix_promo ? (
                      <>
                        <span className="price-promo">{p.prix_promo} €</span>
                        <span className="price-original">{p.prix} €</span>
                      </>
                    ) : (
                      <span>{p.prix} €</span>
                    )}
                  </div>
                  
                  <button 
                    className="btn-outline" 
                    onClick={() => addToCart(p.id)}
                    disabled={p.stock <= 0}
                  >
                    {p.stock > 0 ? "AJOUTER" : "RUPTURE"}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* 4. MANIFESTO BANNER */}
      <section className="manifesto-section" id="manifeste">
        <div className="manifesto-left">
          <div className="manifesto-meta">NOTRE MANIFESTE</div>
          <h2 className="manifesto-title">
            L'Équilibre <span>des Systèmes.</span>
          </h2>
          <p className="manifesto-desc">
            Nous croyons que la beauté n'est pas une surface, mais le résultat d'un système en harmonie. Chaque ingrédient est choisi pour sa fonction structurelle au sein de votre épiderme.
          </p>
        </div>

        <div className="manifesto-right">
          <div className="manifesto-feature">
            <h4 className="feature-title">APPROVISIONNEMENT</h4>
            <p className="feature-desc">Ingrédients sourcés localement en Provence, respectant les cycles de récolte saisonniers.</p>
          </div>
          <div className="manifesto-feature">
            <h4 className="feature-title">CONDITIONNEMENT</h4>
            <p className="feature-desc">Verre ultra léger et papier kraft recyclé à 100%. Aucune trace plastique.</p>
          </div>
          <div className="manifesto-feature">
            <h4 className="feature-title">MÉTHODE</h4>
            <p className="feature-desc">Saponification à froid pendant 6 semaines pour préserver les actifs végétaux.</p>
          </div>
          <div className="manifesto-feature">
            <h4 className="feature-title">VISION</h4>
            <p className="feature-desc">Transformer l'hygiène quotidienne en un acte consciencieux de conception personnelle.</p>
          </div>
        </div>
      </section>

      {/* 5. SHOPPING CART DRAWER */}
      <div className={`cart-drawer-overlay ${isCartOpen ? 'active' : ''}`} onClick={() => setIsCartOpen(false)}>
        <div className="cart-drawer" onClick={(e) => e.stopPropagation()}>
          <div className="cart-header">
            <h3 className="cart-title">Votre Panier</h3>
            <button className="close-btn" onClick={() => setIsCartOpen(false)}><X /></button>
          </div>

          <div className="cart-items">
            {cart && cart.items && cart.items.length > 0 ? (
              cart.items.map(item => (
                <div className="cart-item" key={item.id}>
                  <img 
                    src={item.produit_nom.toLowerCase().includes('huile') ? "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&q=80&w=200" : "https://images.unsplash.com/photo-1607006342411-92fc98c11093?auto=format&fit=crop&q=80&w=200"} 
                    alt={item.produit_nom} 
                    className="cart-item-img" 
                  />
                  <div className="cart-item-info">
                    <h4 className="cart-item-title">{item.produit_nom}</h4>
                    <span className="cart-item-price">{item.prix_unitaire} €</span>
                    <div className="cart-item-qty">
                      <button className="qty-btn" onClick={() => removeFromCart(item.id)}><Minus size={12} /></button>
                      <span>{item.quantite}</span>
                      <button className="qty-btn" onClick={() => addToCart(item.produit, 1)}><Plus size={12} /></button>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div style={{ textAlign: 'center', marginTop: '100px', opacity: 0.6 }}>
                <ShoppingBag size={48} style={{ margin: '0 auto 20px auto' }} />
                <p>Votre panier est encore vide.</p>
              </div>
            )}
          </div>

          {cart && cart.items && cart.items.length > 0 && (
            <div className="cart-footer">
              <div className="cart-total-row">
                <span>Sous-total</span>
                <span>{cart.total} €</span>
              </div>
              <div style={{ display: 'flex', gap: '15px' }}>
                <button className="btn-outline" style={{ flex: 1 }} onClick={clearCart}>VIDER</button>
                <button 
                  className="btn-solid" 
                  style={{ flex: 1 }}
                  onClick={() => { setIsCartOpen(false); setIsCheckoutOpen(true); }}
                >
                  COMMANDER
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 6. AUTHENTICATION MODAL */}
      <div className={`login-modal-overlay ${isAuthOpen ? 'active' : ''}`} onClick={() => setIsAuthOpen(false)}>
        <div className="login-modal" onClick={(e) => e.stopPropagation()}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>{authMode === 'login' ? "Connexion" : "Inscription"}</h3>
            <button className="close-btn" onClick={() => setIsAuthOpen(false)}><X /></button>
          </div>

          {authMode === 'login' ? (
            <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div className="form-group">
                <label>Nom d'utilisateur</label>
                <input 
                  type="text" 
                  required 
                  className="form-input"
                  value={usernameInput}
                  onChange={(e) => setUsernameInput(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Mot de passe</label>
                <input 
                  type="password" 
                  required 
                  className="form-input"
                  value={passwordInput}
                  onChange={(e) => setPasswordInput(e.target.value)}
                />
              </div>
              <button type="submit" className="btn-solid">SE CONNECTER</button>
              <p style={{ fontSize: '13px', textAlign: 'center' }}>
                Nouveau chez sève. ?{' '}
                <a href="#" style={{ color: 'var(--primary-green)', fontWeight: '700' }} onClick={() => setAuthMode('signup')}>Créer un compte</a>
              </p>
            </form>
          ) : (
            <form onSubmit={handleSignup} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <div className="form-group">
                  <label>Prénom</label>
                  <input type="text" required className="form-input" value={firstNameInput} onChange={(e) => setFirstNameInput(e.target.value)} />
                </div>
                <div className="form-group">
                  <label>Nom</label>
                  <input type="text" required className="form-input" value={lastNameInput} onChange={(e) => setLastNameInput(e.target.value)} />
                </div>
              </div>
              <div className="form-group">
                <label>Nom d'utilisateur</label>
                <input type="text" required className="form-input" value={usernameInput} onChange={(e) => setUsernameInput(e.target.value)} />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input type="email" required className="form-input" value={emailInput} onChange={(e) => setEmailInput(e.target.value)} />
              </div>
              <div className="form-group">
                <label>Mot de passe</label>
                <input type="password" required className="form-input" value={passwordInput} onChange={(e) => setPasswordInput(e.target.value)} />
              </div>
              <div className="form-group">
                <label>Confirmer le mot de passe</label>
                <input type="password" required className="form-input" value={confirmPasswordInput} onChange={(e) => setConfirmPasswordInput(e.target.value)} />
              </div>
              <button type="submit" className="btn-solid">S'INSCRIRE</button>
              <p style={{ fontSize: '13px', textAlign: 'center' }}>
                Déjà membre ?{' '}
                <a href="#" style={{ color: 'var(--primary-green)', fontWeight: '700' }} onClick={() => setAuthMode('login')}>Se connecter</a>
              </p>
            </form>
          )}
        </div>
      </div>

      {/* 7. CHECKOUT MODAL */}
      <div className={`login-modal-overlay ${isCheckoutOpen ? 'active' : ''}`} onClick={() => setIsCheckoutOpen(false)}>
        <div className="login-modal" style={{ width: '500px' }} onClick={(e) => e.stopPropagation()}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>Finaliser la Commande</h3>
            <button className="close-btn" onClick={() => setIsCheckoutOpen(false)}><X /></button>
          </div>

          {checkoutError && (
            <div style={{ background: '#f8d7da', color: '#842029', padding: '12px', borderRadius: '8px', fontSize: '14px' }}>
              {checkoutError}
            </div>
          )}

          <form onSubmit={handlePlaceOrder} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div className="form-group">
              <label>Adresse complète de livraison</label>
              <textarea 
                required 
                className="form-input"
                style={{ height: '80px', resize: 'none' }}
                placeholder="N°, Rue, Ville, Région, Pays"
                value={addressText}
                onChange={(e) => setAddressText(e.target.value)}
              />
            </div>
            
            <div style={{ borderTop: '1px solid rgba(11, 48, 35, 0.1)', paddingTop: '20px' }}>
              <div className="cart-total-row" style={{ marginBottom: '20px' }}>
                <span>Total à régler</span>
                <span>{cart ? cart.total : 0} €</span>
              </div>
              <button type="submit" className="btn-solid" style={{ width: '100%' }}>
                CONFIRMER ET PAYER
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* 8. PROFILE SETTINGS PANEL */}
      <div className={`login-modal-overlay ${isProfileOpen ? 'active' : ''}`} onClick={() => setIsProfileOpen(false)}>
        <div className="login-modal" onClick={(e) => e.stopPropagation()}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>Mon Profil</h3>
            <button className="close-btn" onClick={() => setIsProfileOpen(false)}><X /></button>
          </div>

          {profileMessage && (
            <div style={{ background: '#d1e7dd', color: '#0f5132', padding: '10px', borderRadius: '8px', fontSize: '13px' }}>
              {profileMessage}
            </div>
          )}

          <form onSubmit={handleUpdateProfile} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div className="form-group">
              <label>Téléphone</label>
              <input 
                type="text" 
                className="form-input"
                value={phoneInput}
                onChange={(e) => setPhoneInput(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>Biographie</label>
              <textarea 
                className="form-input"
                style={{ height: '70px', resize: 'none' }}
                value={bioInput}
                onChange={(e) => setBioInput(e.target.value)}
              />
            </div>
            <button type="submit" className="btn-solid">SAUVEGARDER</button>
          </form>
        </div>
      </div>
    </div>
  );
}
