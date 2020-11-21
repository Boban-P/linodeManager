from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.

class LinodeSetting(models.Model):
    title = models.CharField(max_length=32, primary_key=True)
    value = models.TextField()

    def __str__(self):
        return "{} => {}".format(self.title, self.value)
    pass

class LinodeTypes(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    title = models.CharField(max_length=128)
    hourlyPrice = models.DecimalField(max_digits=10, decimal_places=4)
    monthlyPrice = models.DecimalField(max_digits=10, decimal_places=2)
    memmory = models.IntegerField()
    disk = models.IntegerField()
    cpu = models.SmallIntegerField()
    gpu = models.SmallIntegerField()
    pass

class LinodeRegions(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    country = models.CharField(max_length=64)
    pass

class LinodeImages(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    title = models.CharField(max_length=128)
    description = models.TextField()
    size = models.SmallIntegerField()
    pass

class LinodeScripts(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    script = models.TextField()
    description = models.CharField(max_length=128)
    pass

class LinodeDomains(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    domain = models.CharField(max_length=64)


class VMclass1(models.Model):
    title = models.CharField(max_length=32, unique=True)
    label = models.CharField(max_length=32, unique=True)
    type = models.ForeignKey(to=LinodeTypes, on_delete=models.CASCADE)
    region = models.ForeignKey(to=LinodeRegions, on_delete=models.CASCADE)
    image = models.ForeignKey(to=LinodeImages, on_delete=models.CASCADE)
    stackscript = models.ForeignKey(to=LinodeScripts, on_delete=models.CASCADE)
    repourl = models.CharField(max_length=256)
    repobranch = models.CharField(max_length=32)
    project = models.CharField(max_length=32)
    domain = models.ForeignKey(to=LinodeDomains, on_delete=models.CASCADE)
    subDomain = models.CharField(max_length=32)
    bucket = models.CharField(max_length=128)
    pass

class VMclass(models.Model):
    class vmTypes(models.TextChoices):
        NANODE   = 'g6-nanode-1', _('Nanode 1GB')
        LINODE_1     = 'g6-standard-1', _('Linode 2GB')
        LINODE_2     = 'g6-standard-2', _('Linode 4GB')
        LINODE_4     = 'g6-standard-4', _('Linode 8GB')
        LINODE_6     = 'g6-standard-6', _('Linode 16GB')
        LINODE_8     = 'g6-standard-8', _('Linode 32GB')
        LINODE_16    = 'g6-standard-16', _('Linode 64GB')
        LINODE_20    = 'g6-standard-20', _('Linode 96GB')
        LINODE_24    = 'g6-standard-24', _('Linode 128GB')
        LINODE_32    = 'g6-standard-32', _('Linode 192GB')
        LINODE_H1    = 'g7-highmem-1', _('Linode 24GB')
        LINODE_H2    = 'g7-highmem-2', _('Linode 48GB')
        LINODE_H4    = 'g7-highmem-4', _('Linode 90GB')
        LINODE_H8    = 'g7-highmem-8', _('Linode 150GB')
        LINODE_H16   = 'g7-highmem-16', _('Linode 300GB')
        DEDICATED_2  = 'g6-dedicated-2', _('Dedicated 4GB')
        DEDICATED_4  = 'g6-dedicated-4', _('Dedicated 8GB')
        DEDICATED_8  = 'g6-dedicated-8', _('Dedicated 16GB')
        DEDICATED_16 = 'g6-dedicated-16', _('Dedicated 32GB')
        DEDICATED_32 = 'g6-dedicated-32', _('Dedicated 64GB')
        DEDICATED_48 = 'g6-dedicated-48', _('Dedicated 96GB')
        DEDICATED_50 = 'g6-dedicated-50', _('Dedicated 128GB')
        DEDICATED_56 = 'g6-dedicated-56', _('Dedicated 256GB')
        DEDICATED_64 = 'g6-dedicated-64', _('Dedicated 512GB')
        GPU_1        = 'g1-gpu-rtx6000-1', _('Dedicated 32GB + RTX6000 GPU x1')
        GPU_2        = 'g1-gpu-rtx6000-2', _('Dedicated 64GB + RTX6000 GPU x2')
        GPU_3        = 'g1-gpu-rtx6000-3', _('Dedicated 96GB + RTX6000 GPU x3')
        GPU_4        = 'g1-gpu-rtx6000-4', _('Dedicated 128GB + RTX6000 GPU x4')

    class vmRegions(models.TextChoices):
        REG_IN  = 'ap-west', _('India')
        REG_CA  = 'ca-central', _('Canada')
        REG_AU  = 'ap-southeast', _('Australia')
        REG_US1 = 'us-central', _('USA-1')
        REG_US2 = 'us-west', _('USA-2')
        REG_US3 = 'us-east', _('USA-3')
        REG_UK  = 'eu-west', _('UK')
        REG_SG  = 'ap-south', _('Singapore')
        REG_DE  = 'eu-central', _('Denmark')
        REG_JP  = 'ap-northeast', _('Japan')
        pass

    class vmImages(models.TextChoices):
        IMG_DEB_10 = 'linode/debian10', _('Debian 10')
        IMG_DEB_08 = 'linode/debian8', _('Debian 8')
        IMG_DEB_09 = 'linode/debian9', _('Debian 9')
        IMG_UBU_16 = 'linode/ubuntu16.04lts', _('Ubuntu 16.04 LTS')
        IMG_UBU_18 = 'linode/ubuntu18.04', _('Ubuntu 18.04 LTS')
        IMG_UBU_20 = 'linode/ubuntu20.04', _('Ubuntu 20.04 LTS')
        IMG_UBU_21 = 'linode/ubuntu20.10', _('Ubuntu 20.10')
        IMG_UBU_14 = 'linode/ubuntu14.04lts', _('Ubuntu 14.04 LTS')
        IMG_UBU_19 = 'linode/ubuntu19.10', _('Ubuntu 19.10')

    title = models.CharField(max_length=32, unique=True)
    label = models.CharField(max_length=32, unique=True)
    type = models.CharField(max_length=32, choices=vmTypes.choices, default=vmTypes.NANODE)
    region = models.CharField(max_length=32, choices=vmRegions.choices, default=vmRegions.REG_SG)
    image = models.CharField(max_length=32, choices=vmImages.choices, default=vmImages.IMG_DEB_10)
    stackscript = models.CharField(max_length=32)
    repourl = models.CharField(max_length=256)
    repobranch = models.CharField(max_length=32)
    repoName = models.CharField(max_length=64)
    project = models.CharField(max_length=32)
    domain = models.CharField(max_length=32)
    subDomain = models.CharField(max_length=32)
    bucket = models.CharField(max_length=128)
    backupfile = models.CharField(max_length=128)
    systemBackup = models.CharField(max_length=128)
    bucketKey = models.CharField(max_length=128)
    bucketSecret = models.CharField(max_length=128)

    def __str__(self):
        return self.title
    pass

class VMInstance(models.Model):
    classInstance = models.ForeignKey(VMclass, models.CASCADE)
    created = models.DateTimeField()
    lastrun = models.DateTimeField()
    backupfile = models.CharField(max_length=128)
    rootPassword = models.CharField(max_length=32)
    state = models.PositiveSmallIntegerField()
    pass
