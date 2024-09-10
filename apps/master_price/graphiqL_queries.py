get_cost_product = """{{
  shop {{
    name
  }}
  productVariant(id: {id}) {{
    id
    inventoryItem {{
      unitCost {{
        amount
      }}
    }}
  }}
}}"""