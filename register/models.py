from django.conf import settings
from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

# ここではusernameの代わりにemailを使うようにUserモデルを継承してカスタマイズします。


class CustomUserManager(UserManager):
    """ユーザーマネージャー"""
    use_in_migrations = True  # manage.pyやobjectsで使用できるようにする

    # 与えられたユーザ名、電子メール、およびパスワードでユーザーを作成して保存する内部関数です
    def _create_user(self, email, password, **extra_fields):
        # emailに値がない場合は、例外メッセージを表示します
        if not email:
            raise ValueError('The given email must be set')

        # ドメイン部分を小文字にしてメールアドレス正規化
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    #  通常ユーザを作る関数です
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    #  スーパーユーザーを作る関数です
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """カスタムユーザーモデル."""

    #  emailフィールドは、テーブル上で一意となる制約を受けます(同じメールアドレスは登録できない)
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    """
    標準のBaseUserManagerを使う代わりに、UserManagerを使うということをDjangoに知らせています。 
    これにより、今後「create_user」、「create_superuser」のメソッドを呼ぶときにUserManagerクラスの
    「create_user」、「create_superuser」のメソッドが呼ばれるようになります。
    """
    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    #  そのユーザーのユニークなキーを記述します
    USERNAME_FIELD = 'email'
    """
    ユーザーを作成するために必要なキーを記述します。
    「createsuperuser management」コマンドを使用してユーザーを作成するとき、プロンプトに
    表示されるフィールド名のリストです。デフォルトは「REQUIRED_FIELDS = [‘username’]」です。
    """
    REQUIRED_FIELDS = []

    class Meta:
        # 管理画面でのオブジェクト表示名
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in
        between."""
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def username(self):
        """username属性のゲッター

        他アプリケーションが、username属性にアクセスした場合に備えて定義
        メールアドレスを返す
        """
        return self.email

# 以下、Userモデルのフィールド（フォーム）を拡張するために
# OneToOneでUserに紐づくProfileモデルを定義します


GENDER_CHOICES = (
    ('1', '女性'),
    ('2', '男性'),
)


class Profile(models.Model):
    name = models.CharField("ハンドルネーム", max_length=255)
    phone = models.CharField("電話番号", max_length=255, blank=True)
    gender = models.CharField("性別", max_length=2, choices=GENDER_CHOICES)
    birthday = models.DateField('生年月日', default=timezone.now)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
