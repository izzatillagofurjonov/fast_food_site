from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Reservation, ContactMessage, NewsletterSubscriber, Order, UserProfile


# ══════════════════════════════════════════════════════════════════════
#  1. RO'YXATDAN O'TISH FORMASI  →  /accounts/register/
# ══════════════════════════════════════════════════════════════════════
class RegisterForm(UserCreationForm):
    """
    Django ning tayyor UserCreationForm dan meros (inherit) olamiz.
    Bu username, password1, password2 maydonlarini avtomatik beradi.
    Biz email va telefon qo'shamiz.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "fctrl", "placeholder": "you@email.com"})
    )
    phone = forms.CharField(
        required=True, max_length=20,
        widget=forms.TextInput(attrs={"class": "fctrl", "placeholder": "+998 90 123 45 67"})
    )

    class Meta:
        model  = User
        fields = ["username", "email", "phone", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "fctrl", "placeholder": "Foydalanuvchi nomi"})
        self.fields["password1"].widget.attrs.update({"class": "fctrl", "placeholder": "Parol"})
        self.fields["password2"].widget.attrs.update({"class": "fctrl", "placeholder": "Parolni takrorlang"})

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu email allaqachon ro'yxatdan o'tgan!")
        return email

    def save(self, commit=True):
        """
        User yaratilgandan keyin avtomatik UserProfile ham yaratamiz.
        """
        user = super().save(commit=commit)
        if commit:
            user.email = self.cleaned_data["email"]
            user.save()
            UserProfile.objects.create(user=user, phone=self.cleaned_data["phone"])
        return user


# ══════════════════════════════════════════════════════════════════════
#  2. KIRISH FORMASI  →  /accounts/login/
# ══════════════════════════════════════════════════════════════════════
class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "fctrl", "placeholder": "Foydalanuvchi nomi"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "fctrl", "placeholder": "Parol"})
    )


# ══════════════════════════════════════════════════════════════════════
#  3. BUYURTMA RASMIYLASHTIRISH FORMASI  →  /cart/checkout/
# ══════════════════════════════════════════════════════════════════════
class OrderForm(forms.ModelForm):
    class Meta:
        model  = Order
        fields = ["full_name", "phone", "address", "payment_method", "comment"]
        widgets = {
            "full_name": forms.TextInput(attrs={
                "class": "fctrl", "placeholder": "Qabul qiluvchi to'liq ismi"
            }),
            "phone": forms.TextInput(attrs={
                "class": "fctrl", "placeholder": "+998 90 123 45 67"
            }),
            "address": forms.Textarea(attrs={
                "class": "fctrl", "rows": 3,
                "placeholder": "Shahar, ko'cha, uy raqami, mo'ljal..."
            }),
            "payment_method": forms.RadioSelect(),
            "comment": forms.Textarea(attrs={
                "class": "fctrl", "rows": 2,
                "placeholder": "Qo'shimcha izoh (ixtiyoriy)..."
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")
        if len(phone) < 7:
            raise forms.ValidationError("Telefon raqami noto'g'ri! Kamida 7 ta raqam bo'lishi kerak.")
        return phone

    def clean_address(self):
        address = self.cleaned_data.get("address", "")
        if len(address) < 10:
            raise forms.ValidationError("Manzilni to'liqroq kiriting (kamida 10 belgi).")
        return address


# ══════════════════════════════════════════════════════════════════════
#  4. STOL BRON QILISH FORMASI  →  HTML: #reservation
# ══════════════════════════════════════════════════════════════════════
class ReservationForm(forms.ModelForm):
    class Meta:
        model  = Reservation
        fields = ["full_name", "phone", "email", "guests", "date", "time", "special_requests"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "fctrl", "placeholder": "John Doe"}),
            "phone": forms.TextInput(attrs={"class": "fctrl", "placeholder": "+1 (800) 000-0000"}),
            "email": forms.EmailInput(attrs={"class": "fctrl", "placeholder": "you@email.com"}),
            "guests": forms.Select(attrs={"class": "fctrl"}),
            "date": forms.DateInput(attrs={"class": "fctrl", "type": "date"}),
            "time": forms.TimeInput(attrs={"class": "fctrl", "type": "time"}),
            "special_requests": forms.Textarea(attrs={
                "class": "fctrl", "rows": 3,
                "placeholder": "Allergiyalar, dietaviy talablar..."
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")
        if len(phone) < 7:
            raise forms.ValidationError("Telefon raqami noto'g'ri!")
        return phone


# ══════════════════════════════════════════════════════════════════════
#  5. BOG'LANISH FORMASI  →  HTML: #contact-section
# ══════════════════════════════════════════════════════════════════════
class ContactForm(forms.ModelForm):
    class Meta:
        model  = ContactMessage
        fields = ["name", "email", "phone", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "fctrl", "placeholder": "John Doe"}),
            "email": forms.EmailInput(attrs={"class": "fctrl", "placeholder": "you@email.com"}),
            "phone": forms.TextInput(attrs={"class": "fctrl", "placeholder": "+1 (800) 000-0000"}),
            "subject": forms.Select(attrs={"class": "fctrl"}),
            "message": forms.Textarea(attrs={"class": "fctrl", "rows": 5, "placeholder": "Xabaringizni yozing..."}),
        }


# ══════════════════════════════════════════════════════════════════════
#  6. NEWSLETTER OBUNA FORMASI  →  HTML: #newsletter
# ══════════════════════════════════════════════════════════════════════
class NewsletterForm(forms.ModelForm):
    class Meta:
        model  = NewsletterSubscriber
        fields = ["email"]
        widgets = {
            "email": forms.EmailInput(attrs={
                "class": "nlinput", "placeholder": "Email manzilingizni kiriting...", "id": "nlEmail"
            })
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if NewsletterSubscriber.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu email allaqachon obuna bo'lgan!")
        return email




