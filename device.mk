LOCAL_PATH := device/alps/ac8257_demo

# Treble : vendor stock Android 9 conserve
PRODUCT_SHIPPING_API_LEVEL := 28
PRODUCT_TARGET_VNDK_VERSION := 28
PRODUCT_EXTRA_VNDK_VERSIONS := 28

PRODUCT_AAPT_CONFIG := normal
PRODUCT_AAPT_PREF_CONFIG := mdpi

DEVICE_PACKAGE_OVERLAYS += $(LOCAL_PATH)/overlay

# fstab
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/rootdir/etc/fstab.ac8257:$(TARGET_COPY_OUT_VENDOR)/etc/fstab.ac8257

# TODO etape 2 : couche Jancar (apps com.jancar.*, service MCU /dev/ttyS1, sepolicy)
# TODO : liste des blobs -> proprietary-files.txt

$(call inherit-product, vendor/alps/ac8257_demo/ac8257_demo-vendor.mk)
