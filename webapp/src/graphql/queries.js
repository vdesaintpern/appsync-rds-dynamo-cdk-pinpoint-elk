/* eslint-disable */
// this is an auto generated file. This will be overwritten

export const getProducts = /* GraphQL */ `
  query GetProducts {
    getProducts {
      id
      name
      price
      imageurl
      brand
      category
      ups
      downs
    }
  }
`;
export const getProduct = /* GraphQL */ `
  query GetProduct($id: ID!) {
    getProduct(id: $id) {
      id
      name
      price
      imageurl
      brand
      category
      ups
      downs
    }
  }
`;
