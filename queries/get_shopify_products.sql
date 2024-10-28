SELECT
	main."id_variantShopi",
	main.id_product,
	main.sku,
	main.cost,
	main.utility,
	main.items_number,
	main.commission_seller,
	main.publicity,
	main.aditional,
	main.packaging_cost,
	main.price_base,
	main.image_link,
	main.title,
	main.inventory_quantity,
	shopi.tags,
	shopi.vendor,
	shopi.status,
	shopi.real_price,
	shopi.compare_at_price,
	shopi.barcode,
	shopi.margen_comparacion_db,
	shopi.commission_platform,
	shopi.category,
	shopi.projected_price,
	shopi.projected_compare_at_price,
	shopi.shipment_cost
FROM
	master_price_mainproducts main
LEFT JOIN master_price_sopifyproducts shopi
ON
	main."id_variantShopi" = shopi."MainProducts_id"