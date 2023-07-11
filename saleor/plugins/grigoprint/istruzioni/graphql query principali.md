#login
##autorization header
`{"Authorization": "JWT <your-access-token>"}`
``` graphql
mutation {
    tokenCreate(email: "grig.griganto@gmail.com", password: "pippo") {   
        token
        refreshToken
        csrfToken
        user {      email    }
        errors {      field      message    }
    }
}
```

