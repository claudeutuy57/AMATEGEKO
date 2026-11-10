from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name_rw = models.CharField(max_length=150, verbose_name="Izina ry'Icyiciro (Kinyarwanda)")
    name_en = models.CharField(max_length=150, verbose_name="Category Name (English)")
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    description_rw = models.TextField(blank=True, verbose_name="Ibisobanuro (Kinyarwanda)")
    description_en = models.TextField(blank=True, verbose_name="Description (English)")
    icon = models.CharField(max_length=50, default="fa-traffic-light", help_text="Font Awesome icon class")
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Syllabus Category"
        verbose_name_plural = "Syllabus Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en or self.name_rw)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order}. {self.name_rw} / {self.name_en}"


class RoadSign(models.Model):
    SIGN_TYPES = [
        ('WARNING', 'Ibyapa Biburira (Warning Signs)'),
        ('PROHIBITION', 'Ibyapa Bibuza (Prohibition Signs)'),
        ('MANDATORY', 'Ibyapa Bitegeka (Mandatory Signs)'),
        ('INFORMATION', 'Ibyapa Bimenyesha (Information Signs)'),
        ('DIRECTION', "Ibyapa by'Icyerekezo (Direction Signs)"),
        ('TEMPORARY', "Ibyapa by'Agateganyo (Temporary Signs)"),
    ]

    sign_type = models.CharField(max_length=20, choices=SIGN_TYPES, verbose_name="Sign Type")
    code = models.CharField(max_length=20, unique=True, verbose_name="Sign Code (e.g., A1, B2a, C1)")
    name_rw = models.CharField(max_length=200, verbose_name="Izina ry'Icyapa (Kinyarwanda)")
    name_en = models.CharField(max_length=200, verbose_name="Sign Name (English)")
    meaning_rw = models.TextField(verbose_name="Icyo Gisobanura (Kinyarwanda)")
    meaning_en = models.TextField(verbose_name="Meaning (English)")
    explanation_rw = models.TextField(blank=True, verbose_name="Ibisobanuro Birambuye n'Amategeko")
    explanation_en = models.TextField(blank=True, verbose_name="Detailed Legal Explanation")
    legal_reference = models.CharField(
        max_length=200, 
        blank=True, 
        default="Iteka rya Perezida N° 85/01 ryo ku wa 02/09/2002",
        verbose_name="Ingingo y'Amategeko (Legal Article)"
    )
    svg_content = models.TextField(
        blank=True, 
        help_text="Vector SVG code for crisp rendering across all screen sizes without asset loading issues"
    )
    image = models.ImageField(upload_to='road_signs/', blank=True, null=True, verbose_name="Uploaded Image")
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['sign_type', 'order', 'code']
        verbose_name = "Road Sign"
        verbose_name_plural = "Road Signs"

    def __str__(self):
        return f"[{self.code}] {self.name_rw} ({self.get_sign_type_display()})"


class Lesson(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='lessons')
    title_rw = models.CharField(max_length=250, verbose_name="Umutwe w'Isomo (Kinyarwanda)")
    title_en = models.CharField(max_length=250, verbose_name="Lesson Title (English)")
    slug = models.SlugField(max_length=260, unique=True, blank=True)
    summary_rw = models.TextField(verbose_name="Incamake (Kinyarwanda)")
    summary_en = models.TextField(verbose_name="Summary (English)")
    content_rw = models.TextField(verbose_name="Isomo Ryose (Kinyarwanda)")
    content_en = models.TextField(verbose_name="Full Lesson (English)")
    key_takeaways_rw = models.TextField(blank=True, verbose_name="Amasomo y'Ingenzi yo Kuzirikana")
    key_takeaways_en = models.TextField(blank=True, verbose_name="Key Takeaways")
    legal_reference = models.CharField(max_length=250, blank=True, verbose_name="Legal Reference")
    estimated_read_time = models.PositiveIntegerField(default=5, help_text="In minutes")
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category__order', 'order']
        verbose_name = "Lesson"
        verbose_name_plural = "Lessons"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title_en or self.title_rw)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title_rw} ({self.category.name_rw})"

