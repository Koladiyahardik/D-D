# D&D Salon Products - E-commerce Website

A luxurious e-commerce website for salon products with a premium dark and gold color theme.

## 🎨 Color Theme

**Primary Colors:**
- **Background:** Dark charcoal (#1A1A1A)
- **Navigation:** Dark gray (#262626)
- **Cards:** Dark gray (#262626) with subtle borders
- **Gold Accent:** Rich gold gradient (#C29B4E to #F0D890)
- **Text:** White and light gray for contrast

**Color Palette:**
- `#1A1A1A` - Main dark background
- `#262626` - Navigation and cards
- `#C29B4E` - Gold mid-tone
- `#F0D890` - Gold highlight
- `#8C6B2F` - Gold shadow/deep tone

## 🚀 Features

- **Responsive Design** - Works on all devices
- **Dark Theme** - Luxurious dark background with gold accents
- **Product Catalog** - Browse products by category
- **Search & Filter** - Find products easily
- **Shopping Cart** - Add/remove items
- **User Authentication** - Login/Register system
- **Order Management** - Place and track orders
- **Admin Panel** - Manage products and orders

## 🛠️ Tech Stack

- **Frontend:** HTML + CSS + Tailwind CSS + JavaScript
- **Backend:** Django (simple views, no REST framework)
- **Database:** SQLite
- **Styling:** Tailwind CSS CDN with custom dark/gold theme

## 📦 Installation

1. **Clone the repository**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

5. **Load sample data:**
   ```bash
   python load_sample_data.py
   ```

6. **Start the server:**
   ```bash
   python manage.py runserver
   ```

## 🌐 Access the Website

- **Website:** http://localhost:8000
- **Admin Panel:** http://localhost:8000/admin
  - Username: `admin`
  - Password: `admin123`

## 📱 Pages

- **Home Page** - Featured products and categories
- **Products Page** - Product listing with filters
- **Product Detail** - Individual product information
- **Cart** - Shopping cart management
- **Checkout** - Order placement
- **Orders** - Order history and tracking

## 🎯 Design Philosophy

The website uses a **luxury salon aesthetic** with:
- Dark backgrounds for sophistication
- Gold accents for premium feel
- Clean typography and spacing
- Smooth animations and transitions
- Mobile-first responsive design

## 🔧 Customization

The color theme can be easily customized by modifying the CSS variables in `templates/base.html`:

```css
.dark-bg { background-color: #1A1A1A; }
.gold-gradient { background: linear-gradient(135deg, #F0D890 0%, #C29B4E 50%, #8C6B2F 100%); }
.gold-accent { color: #F0D890; }
```

## 📞 Support

For support or questions, contact: info@ddsalon.com

---

**D&D Salon Products** - Premium salon products with luxury shopping experience.
