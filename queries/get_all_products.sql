SELECT
	main.id_variantShopi,
	main.id_product,
	main.title,
	main.tags,
	main.vendor,
	main.status,
	main.price,
	main.compare_at_price,
	main.sku,
	main.barcode,
	main.inventory_quantity,
	main.cursor,
	main.costo,
	main.margen_comparacion_db,
	main.kit,
	main.image_link,
	main.category,
	main.items_number,
	mpp.margen,
	mpp.commission_seller,
	mpp.commission_platform,
	mpp.shipping,
	mpp.publicity,
	mpp.aditional
FROM
	master_price_mainproducts main
LEFT JOIN 
master_price_priceengine mpp ON
main.id_variantShopi  = mpp.main_product_id