var AWS = require('aws-sdk');
const Pool = require('pg').Pool

// TODO : parameter or get current region ?
var client = new AWS.SecretsManager({
  region: "<region>"
});

var pool = null;

async function connectToDb() {

  return client.getSecretValue({SecretId: process.env.SECRET_ARN}).promise()
    .then(function(data) {

      var secret= "{}";
    
      if ('SecretString' in data) {
          secret = data.SecretString;
      } 
    
      var secretParsed = JSON.parse(secret);
      password = secretParsed['password'];
      username = secretParsed['username'];
      host = secretParsed['host'];
      database = secretParsed['dbname'];
      port = secretParsed['port'];
    
      pool = new Pool({
        user: username,
        host: host,
        database: database,
        password: password,
        port: port,
      });
    }, 
    function(error) {
      console.log(error);
    });

}

function executeSQL(connection, sql) {
  
  return new Promise((resolve,reject) => {
    connection.query(sql, (err, data) => {
      if (err) {
        return reject(err)
      }
      return resolve(data)
    } )
  })
}

function populateAndSanitizeSQL(sql, variableMapping, connection) {
  Object.entries(variableMapping).forEach(([key, value]) => {
    const escapedValue = value; // TODO: escape
    sql = sql.replace(key, escapedValue);
  });

  return sql;
}

initDB = connectToDb();

exports.handler = async (event) => {

  // this resolves instantly the second time (promised is resolved)
  // TODO : is there to remove this call from the handler completely ?
  await initDB;

  console.log('Received event', JSON.stringify(event, null, 3));
  console.log(pool);

  const inputSQL = populateAndSanitizeSQL(event.sql, event.variableMapping, pool);
  let result = await executeSQL(pool, inputSQL);
  
  console.log(JSON.stringify(result, null, 3));

  return result;
};