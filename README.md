# xblock-rating


1. Tên xblock:  ratingxblock
2. Trong Advanced chọn: Đánh giá khoá học 
3. Deploy xblock vào devstack

Step 1: make lms-shell
Step 2: pip uninstall ratingxblock-xblock #remove xblock cũ nếu bạn đã từng install 
Step 3: pip install git+https://github.com/hopnt-2277/xblock-rating.git
Step 4: exit
Step 5: make studio-shell
Step 6: pip uninstall ratingxblock-xblock
Step 7: pip install git+https://github.com/hopnt-2277/xblock-rating.git
Step 8: exit
Step 9: make lms-restart && make studio-restart

