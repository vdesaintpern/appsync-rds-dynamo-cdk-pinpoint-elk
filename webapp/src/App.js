import React from 'react';
import { 
  BrowserRouter, 
  Route, 
  Link, 
  Switch 
} from 'react-router-dom';
import './App.css';
import Product from './components/productdetail';
import ProductList from './components/productlist';
import { AppBar, Toolbar, Typography, IconButton }  from '@material-ui/core';
import { FastForward } from '@material-ui/icons';
import { makeStyles } from '@material-ui/core/styles';
import Analytics from '@aws-amplify/analytics';

const useStyles = makeStyles((theme) => ({
  grow: {
    flexGrow: 1,
  }
}));

function App() {

  const classes = useStyles();

  function triggerManyEvents() {
    for(var i=0; i < 1000; i++) {
      Analytics.record('event_filling_'+i);
    }    
  };

  return (
    <BrowserRouter>

      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6">
            <Link to="/">Example website</Link>
          </Typography>
          <div className={classes.grow} />
            <IconButton edge="end" onClick={triggerManyEvents}>
              <FastForward style={{ color: '#FFFFFF'}} />
            </IconButton>
        </Toolbar>
      </AppBar>

      
      <div className="App"> 
      </div> 
    
      <Switch>
        <Route exact path='/' component={ProductList}></Route> 
        <Route exact path='/product/:id' component={Product}></Route> 
      </Switch>
    </BrowserRouter> 
  );
}

export default App;
