from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.files import File
from django.db.models import ImageField


# Keep True for the first run.
# This checks your files WITHOUT uploading or changing anything.
DRY_RUN = False


media_root = Path(settings.MEDIA_ROOT).resolve()

found_count = 0
missing_count = 0
uploaded_count = 0

# Avoid uploading the same file more than once during this run.
uploaded_files = {}


print("\nChecking existing image files...\n")


for model in apps.get_models():

    image_fields = [
        field
        for field in model._meta.fields
        if isinstance(field, ImageField)
    ]

    for field in image_fields:

        queryset = model._base_manager.all()

        for instance in queryset.iterator():

            image_field = getattr(instance, field.name)
            old_name = image_field.name

            # Skip empty image fields.
            if not old_name:
                continue

            # Find the original local file.
            local_path = (media_root / old_name).resolve()

            # Prevent paths outside MEDIA_ROOT from being accessed.
            if not local_path.is_relative_to(media_root):
                print(f"SKIPPED unsafe path: {old_name}")
                missing_count += 1
                continue

            if not local_path.is_file():
                print(
                    f"NOT FOUND: "
                    f"{model.__name__}.{field.name} "
                    f"(ID: {instance.pk}) -> {old_name}"
                )
                missing_count += 1
                continue

            found_count += 1

            print(
                f"FOUND: "
                f"{model.__name__}.{field.name} "
                f"(ID: {instance.pk}) -> {old_name}"
            )

            if DRY_RUN:
                continue

            try:
                # Reuse an upload if another record references
                # the same local image during this run.
                if old_name in uploaded_files:
                    cloudinary_name = uploaded_files[old_name]

                else:
                    # Upload the existing local file using the
                    # Cloudinary storage backend configured in Django.
                    with local_path.open("rb") as local_file:

                        cloudinary_name = image_field.storage.save(
                            old_name,
                            File(local_file, name=old_name),
                        )

                    uploaded_files[old_name] = cloudinary_name

                # Update the database record to reference the
                # uploaded image in Cloudinary.
                setattr(instance, field.name, cloudinary_name)

                instance.save(update_fields=[field.name])

                uploaded_count += 1

                print(f"  UPLOADED: {cloudinary_name}")

            except Exception as error:
                print(
                    f"  ERROR uploading {old_name}: {error}"
                )
                raise


print("\n--- SUMMARY ---")
print(f"Local images found: {found_count}")
print(f"Local images missing: {missing_count}")

if DRY_RUN:
    print("\nDRY RUN ONLY: No uploads or database changes were made.")
    print("Review the paths before setting DRY_RUN = False.")
else:
    print(f"Images migrated: {uploaded_count}")
    print("Original local files have NOT been deleted.")