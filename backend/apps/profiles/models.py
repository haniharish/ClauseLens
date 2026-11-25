"""
ClauseLens – UserProfile model.
"""
from django.db import models
from django.conf import settings


class UserProfile(models.Model):
    """
    Extended profile information used by the personalization module
    to calculate clause relevance scores.
    """

    class AgeGroup(models.TextChoices):
        UNDER_13 = 'under_13', 'Under 13'
        TEEN = '13_17', '13–17'
        ADULT = '18_64', '18–64'
        SENIOR = '65_plus', '65+'

    class Jurisdiction(models.TextChoices):
        INDIA = 'india', 'India'
        EU = 'eu', 'EU'
        USA = 'usa', 'USA'
        OTHER = 'other', 'Other'

    INTENDED_USE_CHOICES = [
        ('personal', 'Personal'),
        ('student', 'Student'),
        ('freelancer', 'Freelancer'),
        ('business', 'Business'),
        ('parent_of_minor', 'Parent of Minor'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=True,
    )
    age_group = models.CharField(
        max_length=10,
        choices=AgeGroup.choices,
        default=AgeGroup.ADULT,
    )
    # Stored as comma-separated tags, e.g. "student,personal"
    intended_use = models.CharField(max_length=255, default='personal')
    jurisdiction = models.CharField(
        max_length=10,
        choices=Jurisdiction.choices,
        default=Jurisdiction.OTHER,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'

    def __str__(self):
        return f'Profile({self.user.username})'

    def get_intended_use_list(self):
        """Return intended_use as a Python list."""
        return [tag.strip() for tag in self.intended_use.split(',') if tag.strip()]

    def set_intended_use_list(self, use_list):
        """Accept a list and store as comma-separated string."""
        self.intended_use = ','.join(use_list)
