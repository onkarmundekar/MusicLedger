const http      =   require('http');
const port      =   3000;
const express   =   require("express");
const app       =   express();
const passport  =   require("passport");
const axios     =   require("axios");
var LocalStrategy=  require("passport-local").Strategy;
var bodyParser             =    require("body-parser");
var methodOverride         =    require("method-override");
const { concat } = require('async');

// Middleware
app.use(bodyParser());

// BODY_PARSER and PUBLIC DIRECTORY

app.use(bodyParser.urlencoded({extended:true}));
app.use(express.static(__dirname+"/public"));
app.use(methodOverride("_method"));

// PASSPORT JS CONFIG

app.use(require("express-session")({
    secret:"encode",
    resave:false,
    saveUninitialized:false
}));

app.use(passport.initialize());
app.use(passport.session());

// PASSPORT lOCAL STRATEGY

app.set("view engine","ejs");
//connecting first to second
axios.post('http://localhost:5001/connect_nodes', {
  "nodes":["http://127.0.0.1:5002"]
})
.then(function (response) {
  axios.post('http://localhost:5002/connect_nodes', {
  "nodes":["http://127.0.0.1:5001"]
})
.then(function (response) {
  console.log(response.data);
})
.catch(function (error) {
  console.log(error);
});

  console.log(response.data);
})
.catch(function (error) {
  console.log(error);
});


app.get("/",function(req,res){
    res.render("home2.ejs");
});

app.post("/add_song",(req,res)=>{
    console.log(req.body)
    axios.get('http://localhost:5001/get_chain' ,{})
          .then(function (response) {
              console.log(response.data)
                   let currentchain=response.data.chain;
                   console.log(currentchain.length)
                      
                        for (let i=0;i<currentchain.length;i++){
                           console.log(currentchain[i].song[0])
                
                               if (currentchain[i].song[0].songname == req.body.songname.toUpperCase() ){
                                
                                     return res.send("The song is already present in ledger")
                                    }
                                  }
                                  axios.post('http://localhost:5001/addToBlockChain', {
                                  songname: req.body.songname.toUpperCase(),
                                  artist: req.body.artist,
                               })
                             .then(function (response) {
                                console.log(response.data);
                                axios.get('http://localhost:5001/mine_block' ,{
                             
                                })
                               .then(function (response) {
                                  console.log(response.data);
                                  axios.get('http://localhost:5001/is_valid' ,{
                                 
                                  })
                                 .then(function (response) {
                                    console.log(response.data);
                                    axios.get('http://localhost:5001/get_chain' ,{
                                    })
                                   .then(function (response) {
                                   console.log(response.data); 
                                    
                                  
                                      res.render("chain.ejs",{
                                        chain : response.data.chain,
                                      });
                                  })
                                  
                                  
                                  
                                  .catch(function (error) {
                                   console.log(error);
                                    });
                                  
                                });
                              });
                            });      
        
      })
      .catch(function (error) {
        console.log(error);
      });
 });



app.get("/getcurrentchain",function(req,res){
  axios.get('http://localhost:5001/get_chain' ,{
  })
 .then(function (response) {
 console.log(response.data);
 res.render("chain.ejs",{
  chain : response.data.chain,
});
})

.catch(function (error) {
console.log(error);
});


});

app.listen(3001,function(req,res){
    console.log("Server started");
});

