from django import forms
from django.forms.widgets import DateTimeInput
from .models import CustomUser , MovingCompany , MovingRequest , Adresse, User, Complaint, Dispo

class ClientForm(forms.ModelForm):
	 class Meta:
           model = CustomUser
           exclude = ['date_inscription']

class MovingCompanyForm(forms.ModelForm):
    class Meta:
        model = MovingCompany
        exclude = ['date_inscription', 'limits_reached', 'user', 'devis', 'total_devis','calendar' ]
        widgets = {
        'region': forms.CheckboxSelectMultiple,
        'pays': forms.CheckboxSelectMultiple,
        'service': forms.CheckboxSelectMultiple,
        'date_dispo_debut': forms.DateInput(attrs={'type': 'date'}),
        'date_dispo_fin': forms.DateInput(attrs={'type': 'date'}),
    }

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get("date_dispo_debut")
        date_fin = cleaned_data.get("date_dispo_fin")

        if date_debut and date_fin and date_debut > date_fin:
            raise forms.ValidationError("La date de début doit être antérieure à la date de fin.")

        return cleaned_data


class MovingRequestForm(forms.ModelForm):
    class Meta:
        model = MovingRequest
        exclude = ['limits_reached','adresse_depart', 'adresse_arrivee', 'client', 'total_send'] 
        widgets = {
            'date_dispo_debut': forms.DateInput(attrs={'type': 'date'}),
            'date_dispo_fin': forms.DateInput(attrs={'type': 'date'}),
			'recommendation': forms.Textarea(attrs={'id': 'id_recommendation', 'rows': 4, 'cols': 40}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get("date_dispo_debut")
        date_fin = cleaned_data.get("date_dispo_fin")

        if date_debut and date_fin and date_debut > date_fin:
            raise forms.ValidationError("La date de début doit être antérieure à la date de fin.")

        return cleaned_data

class AdresseForm(forms.ModelForm):
    class Meta:
        model = Adresse
        fields = '__all__'
        #PAs oublier de modifier le multiple choices pour les pays 

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username' , 'email']
    
    def clean_password2(self):
           cd = self.cleaned_data
           if cd['password'] != cd['password2']:
               raise forms.ValidationError('Passwords don\'t match.')
           return cd['password2']
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Un compte avec cette adresse e-mail existe déjà.")
        return email

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        exclude = ['moving_request', 'moving_company', 'date_created']
        widgets = {
            'justification': forms.CheckboxSelectMultiple,
            }

class SearchForm(forms.Form):
    query = forms.CharField()

class DispoForm(forms.ModelForm):
	class Meta:
		model = Dispo
		exclude = ['calendar']
		widgets = {
			'start': DateTimeInput(attrs={'type': 'datetime-local'}),
				'end': DateTimeInput(attrs={'type': 'datetime-local'}),
		}
