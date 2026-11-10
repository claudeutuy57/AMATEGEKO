from django.db import models

class ContactMessage(models.Model):
    name = models.CharField(max_length=150, verbose_name="Amazina (Full Name)")
    email = models.EmailField(verbose_name="Email Address")
    phone = models.CharField(max_length=25, blank=True, verbose_name="Phone Number")
    subject = models.CharField(max_length=200, verbose_name="Subject")
    message = models.TextField(verbose_name="Message")
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.created_at.strftime('%Y-%m-%d')})"

