GET_COST_PRODUCT = """{{
  shop {{
    name
  }}
  productVariant(id: "{id}") {{
    id
    inventoryItem {{
      unitCost {{
        amount
      }}
    }}
  }}
}}"""