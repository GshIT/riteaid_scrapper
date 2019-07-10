# In VPN folder ADD Credentials of torguard, or add your own openvpn files and credentials. credentials must be in a credentials file first row user second row password

1) First you should run get_categories() result data will be in categories.json and in scategories.json, scategories are the end categories
2) then run get_product_links() and the result will be in products_url.json, the file leftscategories.json should have the scategories. here ther shoul be a file named state.json and it start value should be {'state': 1}
3) then run product_scrapper() the result will be in products.json, the file leftproducts.json should have the content of products_url.json.
