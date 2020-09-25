var AWS = require('aws-sdk');

AWS.config.update({region: '<region>'});

var ddb = new AWS.DynamoDB({apiVersion: '2012-08-10'});

exports.handler = async (event) => {

    // Sortkey structure is UP#<date-time-iso> or DOWN#<date-time-iso>
    // This can be improved for production grade applications
    // Still, the # kind of structure in encourage (see dynamoDB resources)
    var voteType = 'UP#'
    if(event.type !== undefined && event.type !== null && event.type=='DOWN') {
        voteType = 'DOWN#'
    }

    return new Promise((resolve,reject) => {

        var params = {
            ExpressionAttributeValues: {
                ':id': {S: event.id},
                ':vote' : {S: voteType}
            },
            KeyConditionExpression: 'productid = :id and begins_with(votesortkey, :vote)',
            TableName: 'votes',
            Select:'COUNT'
        };
    
        ddb.query(params, function(err, data) {
            
            if (err) {
                console.log("Error", err);
                return reject(err)
            } else {
                return resolve(data.Count);
            }
        });
    })

};