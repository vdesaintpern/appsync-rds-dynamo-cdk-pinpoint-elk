// Lambda processing PinPoint items before inserting them into elastic search
// This is linked to the Kinesis Firehose instance

exports.handler = async (event) => {

  const output = event.records.map((record) => {
      
      // Kinesis data is base64 encoded so decode here
      const payload = (Buffer.from(record.data, 'base64')).toString('ascii');
      
      const json_data = JSON.parse(payload);
      
      if(json_data.event_timestamp) {
          json_data.event_timestamp_date = new Date(json_data.event_timestamp);
      }

      if(json_data.attributes) {

        if(json_data.attributes.id) {
          json_data.event_product_id = json_data.attributes.id;
        }

        if(json_data.attributes.name) {
            json_data.event_product_name = json_data.attributes.name;
        }

        if(json_data.attributes.category) {
            json_data.event_product_category = json_data.attributes.category;
        }

        if(json_data.attributes.brand) {
            json_data.event_product_brand = json_data.attributes.brand;
        }

        if(json_data.attributes.price) {
            json_data.event_product_price = json_data.attributes.price;
        }

        if(json_data.attributes.campaign) {
            json_data.event_product_campaign = json_data.attributes.campaign;
        }
      }      
        
      return {
        recordId: record.recordId,
        result: 'Ok',
        data: (Buffer.from(JSON.stringify(json_data))).toString('base64'),
      };
      
  });
  
  return { records: output };
  
};