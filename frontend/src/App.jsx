import React, { useState, useEffect } from 'react';
import { ShoppingBag, User, LogOut, ArrowRight, X, Plus, Minus, Search, Sliders, CheckCircle, ShieldCheck, Heart, Landmark, CreditCard, ChevronRight, BarChart2, Package, Tag, AlertCircle } from 'lucide-react';

const API_URL = 'http://127.0.0.1:8000/api';

// Helper to get or create anonymous session key
const getOrCreateSessionKey = () => {
  let key = localStorage.getItem('session_key');
  if (!key) {
    key = 'session_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
    localStorage.setItem('session_key', key);
  }
  return key;
};

export default function App() {
  const sessionKey = getOrCreateSessionKey();

  // App States
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [cart, setCart] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  // UI Tabs & Views
  const [currentTab, setCurrentTab] = useState('boutique'); // 'boutique' | 'vendeur'
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

  // Checkout address & payment states
  const [countries, setCountries] = useState([]);
  const [regions, setRegions] = useState([]);
  const [cities, setCities] = useState([]);
  const [selectedCountry, setSelectedCountry] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('');
  const [selectedCity, setSelectedCity] = useState('');
  const [streetAddress, setStreetAddress] = useState('');
  
  const [paymentMethod, setPaymentMethod] = useState('stripe'); // 'stripe' | 'wave'
  const [cardNumber, setCardNumber] = useState('');
  const [cardExpiry, setCardExpiry] = useState('');
  const [cardCvc, setCardCvc] = useState('');
  const [mobileNumber, setMobileNumber] = useState('');
  const [isPaying, setIsPaying] = useState(false);
  
  const [orderSuccessId, setOrderSuccessId] = useState('');
  const [checkoutError, setCheckoutError] = useState('');

  // Vendor Dashboard States
  const [vendorProducts, setVendorProducts] = useState([]);
  const [newProductName, setNewProductName] = useState('');
  const [newProductCategory, setNewProductCategory] = useState('');
  const [newProductPrice, setNewProductPrice] = useState('');
  const [newProductPromo, setNewProductPromo] = useState('');
  const [newProductStock, setNewProductStock] = useState('');
  const [newProductDesc, setNewProductDesc] = useState('');

  // Request helper including session headers and credentials
  const apiFetch = (url, options = {}) => {
    const headers = {
      'Content-Type': 'application/json',
      'X-Session-Key': sessionKey,
      ...options.headers,
    };
    return fetch(url, {
      ...options,
      headers,
      credentials: 'include' // Important for HTTP-only cookies
    });
  };

  // 1. Core initialization
  useEffect(() => {
    fetchProducts();
    fetchCategories();
    checkAuthSession();
    fetchCountries();
  }, [selectedCategory, priceMin, priceMax, inStockOnly]);

  // Reload cart whenever auth state changes
  useEffect(() => {
    fetchCart();
  }, [isAuthenticated]);

  // Load geo lookup data
  const fetchCountries = async () => {
    try {
      const res = await apiFetch(`${API_URL}/countries/`);
      if (res.ok) {
        const data = await res.json();
        setCountries(data.results || data);
      }
    } catch (err) {
      console.error("Error fetching countries:", err);
    }
  };

  useEffect(() => {
    if (selectedCountry) {
      fetchRegions(selectedCountry);
      setRegions([]);
      setCities([]);
      setSelectedRegion('');
      setSelectedCity('');
    }
  }, [selectedCountry]);

  const fetchRegions = async (countryId) => {
    try {
      const res = await apiFetch(`${API_URL}/regions/?country=${countryId}`);
      if (res.ok) {
        const data = await res.json();
        setRegions(data.results || data);
      }
    } catch (err) {
      console.error("Error fetching regions:", err);
    }
  };

  useEffect(() => {
    if (selectedRegion) {
      fetchCities(selectedRegion);
      setCities([]);
      setSelectedCity('');
    }
  }, [selectedRegion]);

  const fetchCities = async (regionId) => {
    try {
      const res = await apiFetch(`${API_URL}/cities/?region=${regionId}`);
      if (res.ok) {
        const data = await res.json();
        setCities(data.results || data);
      }
    } catch (err) {
      console.error("Error fetching cities:", err);
    }
  };

  // Fetch products with filters
  const fetchProducts = async () => {
    try {
      let queryParams = [];
      if (selectedCategory) queryParams.push(`categorie=${selectedCategory}`);
      if (priceMin) queryParams.push(`prix_min=${priceMin}`);
      if (priceMax) queryParams.push(`prix_max=${priceMax}`);
      if (inStockOnly) queryParams.push(`en_stock=true`);
      
      const res = await apiFetch(`${API_URL}/produits/?${queryParams.join('&')}`);
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
      const res = await apiFetch(`${API_URL}/categories/`);
      if (res.ok) {
        const data = await res.json();
        setCategories(data.results || data);
      }
    } catch (err) {
      console.error("Error fetching categories:", err);
    }
  };

  // Check if session cookie is active
  const checkAuthSession = async () => {
    try {
      const res = await apiFetch(`${API_URL}/users/me/`);
      if (res.ok) {
        const data = await res.json();
        setCurrentUser(data);
        setIsAuthenticated(true);
        if (data.profil) {
          setPhoneInput(data.profil.telephone || '');
          setBioInput(data.profil.bio || '');
        }
        if (data.is_staff) {
          fetchVendorProducts();
        }
      } else {
        setIsAuthenticated(false);
        setCurrentUser(null);
      }
    } catch (err) {
      setIsAuthenticated(false);
    }
  };

  // Fetch current user cart (dynamic and updated)
  const fetchCart = async () => {
    try {
      const res = await apiFetch(`${API_URL}/panier/mon-panier/`);
      if (res.ok) {
        const data = await res.json();
        setCart(data);
      }
    } catch (err) {
      console.error("Error fetching cart:", err);
    }
  };

  // Fetch vendor products for dashboard
  const fetchVendorProducts = async () => {
    try {
      const res = await apiFetch(`${API_URL}/produits/`);
      if (res.ok) {
        const data = await res.json();
        setVendorProducts(data.results || data);
      }
    } catch (err) {
      console.error("Error fetching vendor products:", err);
    }
  };

  // Login handler setting HTTP-only cookie on success
  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await apiFetch(`${API_URL}/token/`, {
        method: 'POST',
        body: JSON.stringify({ username: usernameInput, password: passwordInput })
      });
      if (res.ok) {
        setIsAuthenticated(true);
        setIsAuthOpen(false);
        // Clear fields
        setUsernameInput('');
        setPasswordInput('');
        checkAuthSession();
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
      const res = await apiFetch(`${API_URL}/users/`, {
        method: 'POST',
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

  // Logout handler clearing sessions
  const handleLogout = () => {
    // Clear cookies by calling refresh view with invalid or simply setting state
    setIsAuthenticated(false);
    setCurrentUser(null);
    setCart(null);
    setIsProfileOpen(false);
    setCurrentTab('boutique');
    // Clear the cookies by reloading or setting expire header if needed
    document.cookie = "access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    document.cookie = "refresh_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    alert("Vous êtes maintenant déconnecté.");
  };

  // Profile update handler
  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    try {
      const res = await apiFetch(`${API_URL}/users/me/`, {
        method: 'PATCH',
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

  // Cart operations (Allowing Anonymous Guests)
  const addToCart = async (productId, qty = 1) => {
    try {
      const res = await apiFetch(`${API_URL}/panier/ajouter/`, {
        method: 'POST',
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
      const res = await apiFetch(`${API_URL}/panier/retirer/`, {
        method: 'POST',
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
      const res = await apiFetch(`${API_URL}/panier/vider/`, {
        method: 'POST'
      });
      if (res.ok) {
        setCart({ ...cart, items: [], total: 0, nombre_articles: 0 });
      }
    } catch (err) {
      console.error("Error clearing cart:", err);
    }
  };

  // Simulated Payment Checkout (Stripe & Mobile Money)
  const handlePlaceOrderWithPayment = async (e) => {
    e.preventDefault();
    setCheckoutError('');
    setIsPaying(true);
    
    // Simulate payment authorization processing
    setTimeout(async () => {
      try {
        const countryObj = countries.find(c => c.id === parseInt(selectedCountry));
        const regionObj = regions.find(r => r.id === parseInt(selectedRegion));
        const cityObj = cities.find(c => c.id === parseInt(selectedCity));
        
        const fullAddress = `${streetAddress}, ${cityObj ? cityObj.name : ''}, ${regionObj ? regionObj.name : ''}, ${countryObj ? countryObj.name : ''}`;
        
        const res = await apiFetch(`${API_URL}/commandes/`, {
          method: 'POST',
          body: JSON.stringify({
            adresse_livraison_texte: fullAddress,
            frais_livraison: 0.00
          })
        });
        
        setIsPaying(false);
        
        if (res.ok) {
          const data = await res.json();
          setOrderSuccessId(data.numero);
          setCart(null);
          setIsCheckoutOpen(false);
          // Reset checkout fields
          setStreetAddress('');
          setSelectedCountry('');
          setSelectedRegion('');
          setSelectedCity('');
        } else {
          const errData = await res.json();
          setCheckoutError(errData.detail || "Le paiement a réussi mais le stock est insuffisant.");
        }
      } catch (err) {
        setIsPaying(false);
        setCheckoutError("Une erreur réseau est survenue.");
      }
    }, 2000);
  };

  // Vendor Dashboard creation of a product
  const handleCreateProduct = async (e) => {
    e.preventDefault();
    try {
      const res = await apiFetch(`${API_URL}/produits/`, {
        method: 'POST',
        body: JSON.stringify({
          nom: newProductName,
          prix: newProductPrice,
          prix_promo: newProductPromo || null,
          stock: newProductStock,
          description: newProductDesc,
          categorie: newProductCategory || null
        })
      });
      if (res.ok) {
        alert("Nouveau cosmétique ajouté au catalogue avec succès !");
        setNewProductName('');
        setNewProductPrice('');
        setNewProductPromo('');
        setNewProductStock('');
        setNewProductDesc('');
        setNewProductCategory('');
        fetchVendorProducts();
        fetchProducts();
      } else {
        const errors = await res.json();
        alert(JSON.stringify(errors));
      }
    } catch (err) {
      console.error("Error creating product:", err);
    }
  };

  // Filter products locally by search query string
  const filteredProducts = products.filter(p => 
    p.nom.toLowerCase().includes(searchQuery.toLowerCase()) || 
    (p.description && p.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div>
      {/* 1. HEADER / NAVBAR */}
      <nav className="navbar">
        <a href="/" className="logo" onClick={(e) => { e.preventDefault(); setCurrentTab('boutique'); }}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--primary-green)' }}>
            <path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2z" />
            <path d="M12 22c0-5.5-4.5-10-10-10" />
            <path d="M12 2c0 5.5 4.5 10 10 10" />
            <circle cx="12" cy="12" r="3" fill="var(--primary-green)" opacity="0.15" />
          </svg>
          sève.
        </a>
        
        <ul className="nav-links">
          <li><a href="#boutique" onClick={() => setCurrentTab('boutique')}>BOUTIQUE</a></li>
          {currentUser && currentUser.is_staff && (
            <li>
              <a 
                href="#vendeur" 
                onClick={() => setCurrentTab('vendeur')}
                style={{ fontWeight: currentTab === 'vendeur' ? '700' : '500', color: 'var(--accent-gold)' }}
              >
                ESPACE VENDEUR
              </a>
            </li>
          )}
          <li><a href="#manifeste">SYSTÈMES</a></li>
          <li><a href="#manifeste">ARCHIVES</a></li>
        </ul>
        
        <div className="navbar-actions">
          {isAuthenticated ? (
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

      {/* 2. SWITCHING BETWEEN STOREFRONT & VENDOR DASHBOARD */}
      {currentTab === 'boutique' ? (
        <>
          {/* HERO SECTION */}
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

          {/* STOREFRONT & CATALOGUE SECTION */}
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
                  <h4 style={{ fontWeight: '700' }}>Paiement & Commande validés !</h4>
                  <p>Votre numéro de commande est : <strong>#{orderSuccessId}</strong>. Nos équipes préparent vos soins cosmétiques.</p>
                </div>
                <button className="btn-outline" style={{ marginLeft: 'auto' }} onClick={() => setOrderSuccessId('')}>OK</button>
              </div>
            )}

            {/* Product Cards Grid */}
            <div className="product-grid">
              {filteredProducts.map(p => {
                let imgUrl = "https://images.unsplash.com/photo-1607006342411-92fc98c11093?auto=format&fit=crop&q=80&w=600";
                if (p.nom.toLowerCase().includes('huile')) {
                  imgUrl = "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&q=80&w=600";
                } else if (p.nom.toLowerCase().includes('baume')) {
                  imgUrl = "https://images.unsplash.com/photo-1601049541289-9b1b7bbbfe19?auto=format&fit=crop&q=80&w=600";
                }
                
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

          {/* MANIFESTO BANNER */}
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
        </>
      ) : (
        /* VENDOR DASHBOARD PANEL */
        <section className="collection-section" style={{ minHeight: '80vh' }}>
          <div className="collection-header" style={{ marginBottom: '40px' }}>
            <div>
              <div className="collection-meta">PANNEL DE GESTION VENDEUR</div>
              <h2 className="collection-title">Espace Partenaire sève.</h2>
            </div>
            <div className="collection-aside">Gérez votre catalogue cosmétique en direct.</div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.8fr', gap: '50px', alignItems: 'start' }}>
            {/* Left: Add new product Form */}
            <div className="login-modal" style={{ width: '100%', boxShadow: 'none', border: '1px solid rgba(11, 48, 35, 0.1)', background: 'white' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: 'var(--primary-green)' }}>
                <Package size={24} />
                <h3 style={{ fontSize: '20px', fontWeight: '700' }}>Nouveau Cosmétique</h3>
              </div>
              
              <form onSubmit={handleCreateProduct} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div className="form-group">
                  <label>Nom du produit</label>
                  <input type="text" required className="form-input" placeholder="ex: Savon à l'Argile Verte" value={newProductName} onChange={(e) => setNewProductName(e.target.value)} />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                  <div className="form-group">
                    <label>Prix (€)</label>
                    <input type="number" step="0.01" required className="form-input" placeholder="36.00" value={newProductPrice} onChange={(e) => setNewProductPrice(e.target.value)} />
                  </div>
                  <div className="form-group">
                    <label>Prix Promo (€)</label>
                    <input type="number" step="0.01" className="form-input" placeholder="Facultatif" value={newProductPromo} onChange={(e) => setNewProductPromo(e.target.value)} />
                  </div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: '10px' }}>
                  <div className="form-group">
                    <label>Catégorie</label>
                    <select className="form-input" value={newProductCategory} onChange={(e) => setNewProductCategory(e.target.value)}>
                      <option value="">Sélectionner</option>
                      {categories.map(c => <option key={c.id} value={c.id}>{c.nom}</option>)}
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Stock</label>
                    <input type="number" required className="form-input" placeholder="10" value={newProductStock} onChange={(e) => setNewProductStock(e.target.value)} />
                  </div>
                </div>
                <div className="form-group">
                  <label>Description botanique</label>
                  <textarea className="form-input" style={{ height: '70px', resize: 'none' }} placeholder="Propriétés et actifs..." value={newProductDesc} onChange={(e) => setNewProductDesc(e.target.value)} />
                </div>
                <button type="submit" className="btn-solid" style={{ marginTop: '10px' }}>AJOUTER AU CATALOGUE</button>
              </form>
            </div>

            {/* Right: Analytics & Products Inventory List */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
              {/* Analytics row */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px' }}>
                <div style={{ background: 'white', padding: '24px', borderRadius: '12px', border: '1px solid rgba(11, 48, 35, 0.08)' }}>
                  <BarChart2 size={24} style={{ color: 'var(--primary-green)', marginBottom: '10px' }} />
                  <div style={{ fontSize: '12px', fontWeight: '600', opacity: 0.6 }}>CHIFFRE D'AFFAIRES</div>
                  <div style={{ fontSize: '28px', fontWeight: '700', color: 'var(--primary-green)' }}>1 840,00 €</div>
                </div>
                <div style={{ background: 'white', padding: '24px', borderRadius: '12px', border: '1px solid rgba(11, 48, 35, 0.08)' }}>
                  <ShoppingBag size={24} style={{ color: 'var(--primary-green)', marginBottom: '10px' }} />
                  <div style={{ fontSize: '12px', fontWeight: '600', opacity: 0.6 }}>SOINS VENDUS</div>
                  <div style={{ fontSize: '28px', fontWeight: '700', color: 'var(--primary-green)' }}>46 unités</div>
                </div>
                <div style={{ background: 'white', padding: '24px', borderRadius: '12px', border: '1px solid rgba(11, 48, 35, 0.08)' }}>
                  <Package size={24} style={{ color: 'var(--primary-green)', marginBottom: '10px' }} />
                  <div style={{ fontSize: '12px', fontWeight: '600', opacity: 0.6 }}>PRODUITS ACTIFS</div>
                  <div style={{ fontSize: '28px', fontWeight: '700', color: 'var(--primary-green)' }}>{vendorProducts.length}</div>
                </div>
              </div>

              {/* Products Table */}
              <div style={{ background: 'white', borderRadius: '16px', border: '1px solid rgba(11, 48, 35, 0.08)', overflow: 'hidden' }}>
                <div style={{ padding: '20px', borderBottom: '1px solid rgba(11, 48, 35, 0.08)', fontWeight: '700', color: 'var(--primary-green)', fontSize: '18px' }}>
                  Inventaire sève.
                </div>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px', textAlign: 'left' }}>
                  <thead>
                    <tr style={{ background: 'rgba(11, 48, 35, 0.02)', borderBottom: '1px solid rgba(11, 48, 35, 0.08)' }}>
                      <th style={{ padding: '16px 20px' }}>Cosmétique</th>
                      <th style={{ padding: '16px 20px' }}>Prix</th>
                      <th style={{ padding: '16px 20px' }}>Stock</th>
                      <th style={{ padding: '16px 20px' }}>Statut</th>
                    </tr>
                  </thead>
                  <tbody>
                    {vendorProducts.map(p => (
                      <tr key={p.id} style={{ borderBottom: '1px solid rgba(11, 48, 35, 0.05)' }}>
                        <td style={{ padding: '16px 20px', fontWeight: '600', color: 'var(--primary-green)' }}>{p.nom}</td>
                        <td style={{ padding: '16px 20px' }}>{p.prix_effectif} €</td>
                        <td style={{ padding: '16px 20px' }}>
                          <span style={{ padding: '4px 8px', background: p.stock > 0 ? '#e3f2fd' : '#ffebee', color: p.stock > 0 ? '#0d47a1' : '#c62828', borderRadius: '4px', fontWeight: '600' }}>
                            {p.stock} U
                          </span>
                        </td>
                        <td style={{ padding: '16px 20px' }}>
                          <span style={{ color: p.actif ? 'green' : 'red', fontWeight: '700' }}>
                            {p.actif ? "En ligne" : "Masqué"}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* 3. SHOPPING CART DRAWER */}
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

      {/* 4. AUTHENTICATION MODAL */}
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

      {/* 5. CHECKOUT DRAWER WITH CASCADING GEO SELECTORS & PAYMENT GATEWAY SIMULATION */}
      <div className={`login-modal-overlay ${isCheckoutOpen ? 'active' : ''}`} onClick={() => setIsCheckoutOpen(false)}>
        <div className="login-modal" style={{ width: '560px' }} onClick={(e) => e.stopPropagation()}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>Finaliser ma Commande</h3>
            <button className="close-btn" onClick={() => setIsCheckoutOpen(false)}><X /></button>
          </div>

          {checkoutError && (
            <div style={{ background: '#f8d7da', color: '#842029', padding: '12px', borderRadius: '8px', fontSize: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <AlertCircle size={16} />
              <span>{checkoutError}</span>
            </div>
          )}

          {isPaying ? (
            <div style={{ textAlign: 'center', padding: '40px 0' }}>
              <div style={{ width: '50px', height: '50px', border: '3px solid var(--gray-pentagon)', borderTopColor: 'var(--primary-green)', borderRadius: '50%', animation: 'spin 1s linear infinite', margin: '0 auto 20px auto' }}></div>
              <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
              <h4 style={{ color: 'var(--primary-green)', fontWeight: '700', fontSize: '18px' }}>Traitement du paiement sécurisé...</h4>
              <p style={{ opacity: 0.7, fontSize: '14px', marginTop: '8px' }}>Veuillez patienter pendant la validation de la transaction.</p>
            </div>
          ) : (
            <form onSubmit={handlePlaceOrderWithPayment} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              {/* Shipping section with live dropdowns */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <h4 style={{ fontSize: '14px', fontWeight: '700', color: 'var(--primary-green)', letterSpacing: '0.05em' }}>ADRESSE DE LIVRAISON</h4>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                  <div className="form-group">
                    <label>Pays</label>
                    <select required className="form-input" value={selectedCountry} onChange={(e) => setSelectedCountry(e.target.value)}>
                      <option value="">Sélectionner</option>
                      {countries.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Région</label>
                    <select required className="form-input" value={selectedRegion} onChange={(e) => setSelectedRegion(e.target.value)} disabled={!selectedCountry}>
                      <option value="">Sélectionner</option>
                      {regions.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
                    </select>
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                  <div className="form-group">
                    <label>Ville</label>
                    <select required className="form-input" value={selectedCity} onChange={(e) => setSelectedCity(e.target.value)} disabled={!selectedRegion}>
                      <option value="">Sélectionner</option>
                      {cities.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Rue & Numéro</label>
                    <input type="text" required className="form-input" placeholder="ex: 12 Rue des Jardins" value={streetAddress} onChange={(e) => setStreetAddress(e.target.value)} />
                  </div>
                </div>
              </div>

              {/* Payment Section */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', borderTop: '1px solid rgba(11, 48, 35, 0.08)', paddingTop: '20px' }}>
                <h4 style={{ fontSize: '14px', fontWeight: '700', color: 'var(--primary-green)', letterSpacing: '0.05em' }}>PASSERELLE DE PAIEMENT SÉCURISÉE</h4>
                
                <div style={{ display: 'flex', gap: '15px', marginBottom: '10px' }}>
                  <button 
                    type="button" 
                    className="btn-outline" 
                    style={{ flex: 1, borderColor: paymentMethod === 'stripe' ? 'var(--primary-green)' : 'rgba(11, 48, 35, 0.2)', background: paymentMethod === 'stripe' ? 'rgba(11, 48, 35, 0.05)' : 'transparent' }}
                    onClick={() => setPaymentMethod('stripe')}
                  >
                    <CreditCard size={16} style={{ marginRight: '8px' }} />
                    Stripe / CB
                  </button>
                  <button 
                    type="button" 
                    className="btn-outline" 
                    style={{ flex: 1, borderColor: paymentMethod === 'wave' ? 'var(--primary-green)' : 'rgba(11, 48, 35, 0.2)', background: paymentMethod === 'wave' ? 'rgba(11, 48, 35, 0.05)' : 'transparent' }}
                    onClick={() => setPaymentMethod('wave')}
                  >
                    <Landmark size={16} style={{ marginRight: '8px' }} />
                    Wave / Mobile
                  </button>
                </div>

                {paymentMethod === 'stripe' ? (
                  <div style={{ background: 'white', padding: '16px', borderRadius: '8px', border: '1px solid rgba(11, 48, 35, 0.1)', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <div className="form-group">
                      <label>Numéro de carte</label>
                      <input type="text" required className="form-input" placeholder="4242 4242 4242 4242" value={cardNumber} onChange={(e) => setCardNumber(e.target.value)} />
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: '10px' }}>
                      <div className="form-group">
                        <label>Expiration</label>
                        <input type="text" required className="form-input" placeholder="MM/AA" value={cardExpiry} onChange={(e) => setCardExpiry(e.target.value)} />
                      </div>
                      <div className="form-group">
                        <label>CVC</label>
                        <input type="text" required className="form-input" placeholder="123" value={cardCvc} onChange={(e) => setCardCvc(e.target.value)} />
                      </div>
                    </div>
                  </div>
                ) : (
                  <div style={{ background: 'white', padding: '16px', borderRadius: '8px', border: '1px solid rgba(11, 48, 35, 0.1)', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <div className="form-group">
                      <label>Numéro de Téléphone (Paiement Mobile)</label>
                      <input type="text" required className="form-input" placeholder="+225 07 00 00 00 00" value={mobileNumber} onChange={(e) => setMobileNumber(e.target.value)} />
                    </div>
                    <p style={{ fontSize: '11px', opacity: 0.6 }}>Une notification de validation sera envoyée sur votre mobile Wave / Mobile Money.</p>
                  </div>
                )}
              </div>
              
              <div style={{ borderTop: '1px solid rgba(11, 48, 35, 0.08)', paddingTop: '20px' }}>
                <div className="cart-total-row" style={{ marginBottom: '20px' }}>
                  <span>Total à régler</span>
                  <span>{cart ? cart.total : 0} €</span>
                </div>
                <button type="submit" className="btn-solid" style={{ width: '100%' }}>
                  AUTORISER LA TRANSACTION
                </button>
              </div>
            </form>
          )}
        </div>
      </div>

      {/* 6. PROFILE SETTINGS PANEL */}
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
