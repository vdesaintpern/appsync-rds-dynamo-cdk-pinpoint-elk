import { Container, IconButton, makeStyles, Typography } from '@material-ui/core';
import { API, graphqlOperation } from 'aws-amplify';
import React, { useEffect, useState } from 'react'; 
import { Link, useParams } from 'react-router-dom';
import * as subscriptions from '../graphql/subscriptions';
import * as mutations from '../graphql/mutations';
import Analytics from '@aws-amplify/analytics';
import queryString from 'query-string';
import { ThumbDown, ThumbUp } from '@material-ui/icons';

const useStyles = makeStyles((theme) => ({
    root: {
        width: '100%',
        display: 'flex',
        flexDirection: 'row',
        margin: 10
    },
    media: {
        width: 250,
        height: 145,
        margin: 5
    },
    content: {
        
    },
    nav: {
        fontStyle: 'italic',
        marginTop: 10,
        marginBottom: 10,
        textDecoration: 'underline'
    }
}));

// Example of manual query - useful when you want to query less fields 
export const getProductWithUpdAndDown = /* GraphQL */ `
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

function Product(props) {

    const classes = useStyles();
    const id  = useParams().id;

    const [data, setData] = useState({ product: []});

    const queryStringParsed = queryString.parse(props.location.search);
    
    // campaign attribute will be added to events when ?campaign=XXX is passed to the page
    var campaign = '';
    if(queryStringParsed.campaign !== undefined) {
        campaign=queryStringParsed.campaign; 
    }

    useEffect(() => {
        
        const fetchProduct = async () => {
            const response = await API.graphql(graphqlOperation(getProductWithUpdAndDown, { id: id }));
            setData({ product: response.data.getProduct});

            subscribeProductChanged(response.data.getProduct.id);

            Analytics.record({
                name: 'load-product',
                attributes: { id: id, name: response.data.getProduct.name, category: response.data.getProduct.category, brand: response.data.getProduct.brand, price: response.data.getProduct.price, campaign: campaign }
            });
        };

        fetchProduct();
        

    },[id]);

    function thumbUp() {
        
        API.graphql(graphqlOperation(mutations.voteUp, { id: id }));

        Analytics.record({
            name: 'upvote-product',
            attributes: { id: data.product.id, name: data.product.name, category: data.product.category, brand: data.product.brand, price: data.product.price, campaign: campaign }
        });


    };

    function thumbDown() {
        
        API.graphql(graphqlOperation(mutations.voteDown, { id: id }));

        Analytics.record({
            name: 'downvote-product',
            attributes: { id: data.product.id, name: data.product.name, category: data.product.category, brand: data.product.brand, price: data.product.price, campaign: campaign }
        });        
    };

    function subscribeProductChanged(id) {

        API.graphql(graphqlOperation(subscriptions.productVoteChanged, { id: id }))
            .subscribe({
                next: (eventData) => {
                console.log("vote changed");
                console.log(eventData);
                setData({ product: eventData.value.data.productVoteChanged});
            }
        });
    };

    return (
        
        <Container maxWidth="sm">
            <div className={classes.nav}>
                <Link to="/">&lt;- Back to list of product</Link>
            </div>
        
            <Typography variant="h5" component="h5">
                { data.product.name }
            </Typography>

            <Typography variant="subtitle2" color="textSecondary">
                { data.product.brand }
            </Typography>

            <img src={data.product.imageurl} width='300px' alt=""/>

            <Typography variant="subtitle2" color="textSecondary">
                ${data.product.price}
            </Typography>
            
            <IconButton onClick={thumbUp}>
                {data.product.ups}&nbsp; <ThumbUp style={{ color: '#00FF00'}} />
            </IconButton>

            <IconButton onClick={thumbDown}>
                {data.product.downs}&nbsp; <ThumbDown style={{ color: '#FF0000'}} />
            </IconButton>
        </Container>
        
    )
    
}

export default Product; 