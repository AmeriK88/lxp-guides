# 🚀 Lanzaxperience

A modern SaaS platform connecting travelers with local guides for unforgettable experiences. Built with Django and styled with Tailwind CSS, this app empowers guides to showcase their expertise and travelers to discover authentic adventures.

![Lanzaxperience Logo](https://img.shields.io/badge/Lanzaxperience-Experience%20Booking-blue?style=for-the-badge&logo=map&logoColor=white) ![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white) ![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)

## 🌟 Features

- **User Management**: Secure registration and login for guides and travelers.
- **Experience Listings**: Guides can create and manage detailed experience profiles with photos and descriptions.
- **Booking System**: Seamless booking process with availability management and real-time updates.
- **Reviews & Ratings**: Travelers can leave feedback to help others choose the best experiences.
- **Dashboard**: Personalized dashboards for guides and travelers to manage bookings and profiles.
- **Responsive Design**: Mobile-friendly interface powered by Tailwind CSS.
- **Email Notifications**: Automated emails for booking confirmations and updates.

## 🛠 Tech Stack

- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, JavaScript, Tailwind CSS
- **Database**: SQLite (development), PostgreSQL (production)
- **Deployment**: Ready for Heroku, AWS, or similar
- **Other Tools**: Node.js for asset compilation, Git for version control

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/lanzaxperience.git
   cd lanzaxperience
   ```

2. **Set up Python environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up Node.js for Tailwind**:
   ```bash
   npm install
   npx tailwindcss -i ./src/input.css -o ./static/css/tailwind.css --watch
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser**:
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the server**:
   ```bash
   python manage.py runserver
   ```

Visit `http://127.0.0.1:8000` to see the app in action!

## 🚀 Usage

- Register as a guide or traveler.
- Guides: Create experiences, set availability, and manage bookings.
- Travelers: Browse experiences, make bookings, and leave reviews.
- Admins: Use Django admin for oversight.

## 🤝 Contributing

Contributions are welcome! Please fork the repo, create a feature branch, and submit a pull request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


---

Made by the Lanzaxperience team. Happy adventuring! 🌍✈️