SELECT
		main.*,
		count(sodi.main_product_id) as main_sodi,
		COUNT(meli.main_product_id) as main_meli
FROM
	master_price_mainproducts main
left join master_price_productssodimac sodi 
    on
	main.id_variantShopi = sodi.main_product_id
left join master_price_productsmeli meli 
    on
	main.sku = meli.sku 
GROUP BY  1
