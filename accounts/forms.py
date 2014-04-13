from django import forms
from accounts.models import Account


class CreateAccountForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = [
            'email',
            'first_name',
            'last_name',
            'user_designation',
            'permission_irf_view',
            'permission_irf_add',
            'permission_irf_edit',
            'permission_vif_view',
            'permission_vif_add',
            'permission_vif_edit',
            'permission_accounts_view',
            'permission_accounts_add',
            'permission_accounts_edit',
            'permission_accounts_defaults',
        ]

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        account = super(CreateAccountForm, self).save(commit=False)
        account.set_password(self.cleaned_data["password1"])
        if commit:
            account.save()
        return account
