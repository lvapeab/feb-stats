const express = require('express');
const hbs = require('hbs');
var busboy = require('connect-busboy'); //middleware for form/file upload
var path = require('path');     //used for file path
const dateFormat = require('date-format');

var argv = require('yargs')
    .default('grpc_address', "stats-analyzer") //process.env.GRPC_ADDRESS)
    .default('grpc_port', process.env.GRPC_PORT)
    .default('port', process.env.WEB_PORT)
    .argv
;

var fs = require('fs-extra');       //File System - for file manipulation
var grpc = require('grpc');
// var PROTO_PATH = __dirname + '../../../protos/feb_stats.proto';
var PROTO_PATH = "protos/feb_stats.proto";

var protoLoader = require('@grpc/proto-loader');
var packageDefinition = protoLoader.loadSync(
    PROTO_PATH,
    {
        keepCase: true,
        longs: String,
        enums: String,
        defaults: true,
        oneofs: true
    });

var feb_stats_proto = grpc.loadPackageDefinition(packageDefinition).feb_stats;
let grpc_options = {
    'grpc.max_receive_message_length': 15 * 1024 * 1024,
    'grpc.max_send_message_length': 15 * 1024 * 1024
};
var client = new feb_stats_proto.FebStatsService(argv.grpc_address + ':' + argv.grpc_port,
    grpc.credentials.createInsecure(),
    grpc_options);

console.log("Starting server in: " + argv.grpc_address + ':' + argv.grpc_port);

const app = express();
app.use(busboy());
app.use(express.static('js/node/style'));  // serve files from the public directory
app.use(express.static('js/node/config'));  // serve files from the public directory

// app.engine('.hbs', exphbs({extname: '.hbs'}));
app.set('views', 'js/node/views');
app.set('view engine', '.hbs');
app.get('/', (req, res) => {
    return res.render('index.hbs', {layout: false});
});

function getByteArrayFromFilePath(filePath) {
    let fileData = fs.readFileSync(filePath).toString('hex');
    let result = [];
    for (var i = 0; i < fileData.length; i += 2)
        result.push('0x' + fileData[i] + '' + fileData[i + 1]);
    return result;
}

// Create a Route (/upload) to handle the Form submission (handle POST requests to /upload)
var uploaded_files = [];  // TODO: Find a better way to manage this.
app.route('/upload').post(function (req, res, next) {
    var fstream;
    req.pipe(req.busboy);
    req.busboy.on('file', function (fieldname, file, filename) {
        console.log("Uploading: " + filename);
        //Path where image will be uploaded
        var path_to_upload = path.join(__dirname, 'uploads', filename);
        uploaded_files.push(path_to_upload);
        fstream = fs.createWriteStream(path_to_upload);
        file.pipe(fstream);
        fstream.once('close', function () {
            console.log("Upload Finished of " + filename);
            res.end('File have been uploded');
        });
    });
});

app.route('/analyze').post(function (req, res, next) {
    var data = [];
    console.log("Processing: " + uploaded_files.length + " files!");
    for (i = 0; i < uploaded_files.length; i++) {
        data.push(getByteArrayFromFilePath(uploaded_files[i]));
        fs.unlink(uploaded_files[i], (err) => {
            if (err) {
                console.error(err);
            }
        });
    }
    uploaded_files = [];
    client.GetFebStats({boxscores: data}, function (err, response) {

        if (typeof response === 'undefined')  {
            console.log('Undefined response.');
            console.log('Error:', err);

        } else {
            console.log('Response:', response);
            var filename = new Date();
            filename = dateFormat(filename, "dd_mm_yyyy_h:MM");
            res.writeHead(200, {
                    'Content-Type': 'application/vnd.ms-excel',
                    'Content-disposition': 'attachment; filename=' + 'estadisticas_' + filename + '.xlsx',
                    'Content-Length': response['sheet'].length
                }
            );
            res.end(response['sheet']);
        }
    });

});

app.listen(argv.port, () => {
    console.log('Express server listening on port ' + argv.port);
});
