# xblock-rating

Tên xblock: ratingxblock

Trong Advanced chọn: Đánh giá khoá học

## INSTALL IN NATIVE

# To install the xblock:

sudo -H -u edxapp bash

source /edx/app/edxapp/edxapp_env

pip install git+https://github.com/framgia/MOOC_General.git@ratingxblock-master

# To uninstall the xblock

pip uninstall ratingxblock-xblock

# Reset server 

sudo /edx/bin/edxapp-update-assets

sudo /edx/bin/supervisorctl restart lms

sudo /edx/bin/supervisorctl restart cms


# Deploy xblock vào devstack

Step 1: make lms-shell

Step 2: pip uninstall ratingxblock-xblock #remove xblock cũ nếu bạn đã từng install

Step 3: pip install git+https://github.com/framgia/MOOC_General.git@ratingxblock-master

Step 4: exit

Step 5: make studio-shell

Step 6: pip uninstall ratingxblock-xblock

Step 7: pip install git+https://github.com/framgia/MOOC_General.git@ratingxblock-master

Step 8: exit

Step 9: make lms-restart && make studio-restart





