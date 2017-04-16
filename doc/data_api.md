# Purchases API

API methods for Acme Megastore

## Data source

The file `acme/data/data.json` contains a ready to use data set.

If you want to generate a new batch of data, you can use the 
`acme/data/generator.py` script. Just dump its output into the 
aforementioned `data.json` file.

## API Reference

### GET purchases/by_user/:username

- params:
  - username (string)
  - ?skip (int)
  - ?limit (int)

- response (json):

```
{
  "purchases": [
    {
      "id": (int),
      "product_id": (int),
      "username": (string),
      "date": (iso8601 string)
    },
    ...
  ]
}
```

### GET purchases/by_product/:product_id

- params:
  - product_id (int)
  - ?skip (int)
  - ?limit (int)

- response: same as `GET purchases/by_user/:username`

### GET products

- params:
  - ?skip (int)
  - ?limit (int)

- response (json):

```
{
  "products": [
    {
      "id": (int),
      "face": (string),
      "size": (int),
      "price": (int)
    }
  ]
}
```


### GET products/:id

- params:
  - id (int)

- response (json):

```
{
  "product": {
    "id": (int),
    "face": (string),
    "size": (int),
    "price": (int)
  }
}
```

### GET users

- params:
  - ?skip (int)
  - ?limit (int)

- response (json):

```
{
  "users": [
    {
      "username": (string),
      "email": (string)
    },
    ...
  ]
}
```

### GET users/:username

- params:
  - username (string)

- response (json):

```
{
  "user": {
    "username": (string),
    "email": (string)
  }
}
```