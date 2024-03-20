from django.db import models

class IllnessDetail(models.Model):
    EYE = 'EY'
    EAR = 'ER'
    NOSE = 'NS'
    SKIN = 'SK'
    DENTAL = 'DT'
    BONE = 'BN'
    MALARIA = 'ML'
    TYPHOID = 'TY'
    DIABETES = 'DB'
    URINARY_TRACT_INFECTION = 'UTI'
    SEX_ORGAN_ILLNESS = 'SOI' 
    BODY_PART_CHOICES = [
        (EYE, 'eye'),
        (EAR, 'ear'),
        (NOSE, 'nose'),
        (SKIN, 'skin'),
        (DENTAL, 'mouth&dental'),
        (BONE, 'bone')
    ]
    SPECIFIC_ILLNESS_CHOICES = [
        (MALARIA, 'malaria'),
        (TYPHOID, 'typhoid'),
        (DIABETES, 'diabetes'),
        (URINARY_TRACT_INFECTION, 'urinary tract infection'),
        (SEX_ORGAN_ILLNESS, 'sex organ illness'),
    ]
    body_part = models.CharField(choices=BODY_PART_CHOICES, blank=True, null=True)
    illness = models.CharField(choices=SPECIFIC_ILLNESS_CHOICES, blank=True, null=True)
    age = models.IntegerField(blank=False, null=False)

    def __str__(self):
        return f"illness detail {self.id}"


