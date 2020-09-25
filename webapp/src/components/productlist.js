import React, { useEffect, useState } from 'react'; 
import { Link } from 'react-router-dom';
import { API, graphqlOperation } from 'aws-amplify';
import * as queries from '../graphql/queries';
import { Card, CardContent, CardMedia, Container, makeStyles, Typography } from '@material-ui/core';
import Analytics from '@aws-amplify/analytics';

const useStyles = makeStyles((theme) => ({
    root: {
        width: '100%',
        display: 'flex',
        flexDirection: 'row',
        margin: 10,
        '&:hover': {
            backgroundColor: '#EEEEEE'
        }
    },
    media: {
        width: 250,
        height: 145,
        margin: 5
    },
    content: {
        
    }
}));

function ProductList() {

    const classes = useStyles();

    const [data, setData] = useState({ products: []});

    useEffect(() => {

        Analytics.record('fetch-product-list');

        const fetchProducts = async () => {
            const response = await API.graphql(graphqlOperation(queries.getProducts));
            setData({ products: response.data.getProducts});
        };

        fetchProducts();

    },[]);

    return (
        <Container maxWidth="sm">
        {
                data.products.map(function(item) {
                    return <Link to={{ pathname:'/product/' + item.id }} key={item.id}>
                        <Card className={classes.root}>
                            <CardMedia
                                    className={classes.media}
                                    image={item.imageurl}
                                    title={item.name}
                                />

                            <CardContent className={classes.content}>
                                <Typography variant="subtitle1">
                                    {item.name}
                                </Typography>
                                <Typography variant="subtitle2" color="textSecondary">
                                {item.category}
                                </Typography>
                                <Typography variant="h4">
                                    ${item.price}
                                </Typography>
                            </CardContent>
                        </Card>
                    </Link>
                })
            }
        </Container>
    )
    
} 

export default ProductList; 