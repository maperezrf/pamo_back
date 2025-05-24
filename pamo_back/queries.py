GET_DRAFT_ORDERS = """
query {{
  draftOrders(first: 250 {cursor}){{
    pageInfo {{
      hasNextPage
      endCursor
    }}
    edges {{
      node {{
        id
        name
        createdAt
        updatedAt
        totalPrice
        customer {{
          firstName
          lastName
        }}
      }}
    }}
  }}
}}
"""

GET_DRAFT_ORDER = """
{{
  draftOrders(first: 1 query:"id:{}") {{
    edges {{
      node {{
        id
        name
        totalPrice
        createdAt
        updatedAt
          appliedDiscount {{
            amount
            title
        }}
        customer {{
          displayName
          email
          defaultAddress {{
            company
            phone
          }}
          metafields(first: 200, namespace: "custom") {{
            edges {{
              node {{
                key
                value
              }}
            }}
          }}
        }}
        invoiceUrl
        lineItems(first: 250) {{
          edges {{
            node {{
              title
              originalUnitPrice
              quantity
              product {{
                images(first: 1) {{
                  edges {{
                    node {{
                      originalSrc
                    }}
                  }}
                }}
                variants(first: 1) {{ 
                  edges {{
                    node {{
                      sku
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
      }}
    }}
  }}
}}
"""

GET_DRAFT_ORDER_UPDATE = """
{{
  draftOrders(first: 1 query:"id:{}") {{
    edges {{
      node {{
        id
        name
        createdAt
        updatedAt
        totalPrice
        customer {{
          firstName
          lastName
        }}
      }}
    }}
  }}
}}
"""

GET_PRODUCTS ="""
{{
  products(first: 249 {cursor}) {{
    pageInfo {{
      hasNextPage
      endCursor
    }}
    edges {{
      node {{
        id
        tags
        title
        vendor
        status
        variants(first: 250) {{
          edges {{
            node {{
              id
              price
              compareAtPrice
              sku
              barcode
              inventoryQuantity
              image {{
                src
              }}
            }}
          }}
        }}
        images(first: 1) {{
          nodes {{
            src
          }}
        }}
        category {{
          fullName
        }}
      }}
    }}
  }}
}}"""

UPDATE_QUERY = """mutation UpdateProductAndVariantAndAdjustInventory(
  {productInput}
  {variantInput}
  {inventoryAdjustInput}
  ){{
  {productUpdateq}
  {productVariantUpdateq}
  {inventoryAdjustQuantity}
}}"""

UPTADE_PRODUCT = """
  productUpdate(input: $productInput) {
    userErrors {
      field
      message
    }
  }
"""

PRODUCT_VARIANT_UPDATE = """
  productVariantUpdate(input: $variantInput) {
    userErrors {
      field
      message
    }
  }
"""

INVENTORY_ADJUST ="""
  inventoryAdjustQuantity(input: $inventoryAdjustInput) {
  inventoryLevel {
    available
    }
  }
"""

GET_VARIANT_ID = """{{
products(first: 1, query: "sku:{skus}") {{
    edges {{
    node {{
        id
        variants(first: 1) {{
        edges {{
            node {{
            id
            sku
            }}
        }}
        }}
    }}
    }}
}}
}}
"""

GET_INVENTORY = """
{{
products(first: 1, query: "sku:{sku}") {{
    edges {{
    node {{
        id
        variants(first: 1) {{
        edges {{
            node {{
            sku
            inventoryQuantity
            }}
        }}
        }}
    }}
    }}
}}
}}
"""



GET_VARIANT = """
{{
  productVariant(id: "{id}") {{
    id
    price
    compareAtPrice
    sku
    barcode
    inventoryQuantity
    inventoryItem {{
      id
      inventoryLevels(first: 1) {{
        edges {{
          node {{
            id
          }}
        }}
      }}
    }}
  }}
}}
"""

GET_PRODUCT= """
query {{
   product(id : "gid://shopify/Product/{id}") {{
          id
        	tags
          title
          vendor
          status
          published: publishedInContext(context: {{country: CO}})
          variants(first: 250) {{
      edges {{
        node {{
          id
        }}
      }}
    }}
  }}
}}
  """

GET_PRODUCTS_FULL = """{{
  products(first: 250, query: "sku:{sku}") {{
    edges {{
      node {{
        id
        title
        tags
        vendor
        status
        published: publishedInContext(context: {{country: CO}})
        variants(first: 250) {{
          edges {{
            node {{
              id
              sku
              barcode
              inventoryQuantity
              inventoryItem {{
                id
                inventoryLevels(first: 1) {{
                  edges {{
                    node {{
                      id
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
      }}
    }}
  }}
}}"""


CREATION_BULK = '''mutation {
  bulkOperationRunQuery(
    query: """
          {
      products(first: 1) {
        pageInfo {
          hasNextPage
          endCursor
        }
        edges {
          node {
            id
            tags
            title
            vendor
            status
            variants(first: 250) {
              edges {
                node {
                  id
                  price
                  compareAtPrice
                  sku
                  barcode
                  inventoryQuantity
                  image {
                    src
                  }
                  inventoryItem {
                    unitCost {
                      amount
                    }
                  }
                }
              }
            }
            images(first: 1) {
              edges {
                node {
                  src
                }
              }
            }
            category {
              fullName
            }
          }
        }
      }
    }
    """
  ) {
    bulkOperation {
      id
      status
    }
    userErrors {
      field
      message
    }
  }
}'''

REQUEST_FINISH_BULK = """{
  currentBulkOperation {
    id
    status
    errorCode
    createdAt
    completedAt
    url
  }
}"""


CREATE_CUSTOMER = """
mutation customerCreate($customer: CustomerInput!) {
  customerCreate(input: $customer) {
    customer {
      id
      email
    }
    userErrors {
      message
    }
  }
}
"""
CUSTOMER_DATA = """
{"customer": {
  "firstName": "test",
  "lastName": "test",
  "email": "test@test.com",
  "addresses": [
    {
      "address1": "test",
      "city": "Bogota",
      "company": "empresa test"
    }
  ]
}
}
"""