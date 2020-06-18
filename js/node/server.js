const express = require('express');
var busboy = require('connect-busboy'); //middleware for form/file upload
var path = require('path');     //used for file path
const exphbs = require('express-handlebars');
var events = require('events');

var fs = require('fs-extra');       //File System - for file manipulation
var grpc = require('grpc');
var PROTO_PATH = __dirname + '../../../protos/feb_stats.proto';

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
var client = new feb_stats_proto.FebStatsService('localhost:50001', grpc.credentials.createInsecure());


const app = express();
app.use(busboy());
app.use(express.static(path.join(__dirname, 'public')));  // serve files from the public directory

app.engine('.hbs', exphbs({extname: '.hbs'}));
app.set('view engine', '.hbs');
app.get('/', (req, res) => {
    return res.render('index', {layout: false});
});

// app.use(express.urlencoded({extended: true}));
function getByteArrayFromFilePath(filePath) {
    let fileData = fs.readFileSync(filePath).toString('hex');
    let result = [];
    for (var i = 0; i < fileData.length; i += 2)
        result.push('0x' + fileData[i] + '' + fileData[i + 1]);
    return result;
}

/* ==========================================================
Create a Route (/upload) to handle the Form submission
(handle POST requests to /upload)
Express v4  Route definition
============================================================ */
var uploaded_files = [];
app.route('/upload').post(function (req, res, next) {
        var fstream;
        req.pipe(req.busboy);
        req.busboy.on('file', function (fieldname, file, filename) {
            console.log("Uploading: " + filename);
            // var array = fs.readFileSync(file).toString('latin1');
            //Path where image will be uploaded
            var path_to_upload = __dirname + '/uploads/' + filename;
            uploaded_files.push(path_to_upload);
            fstream = fs.createWriteStream(path_to_upload);
            file.pipe(fstream);
            fstream.on('close', function () {
                console.log("Upload Finished of " + filename);
                // res.end()
            });
        });
 });

app.route('/analyze').post(function (req, res, next) {
        var data = [];
        for (i=0; i< uploaded_files.length; i++){
            data.push(getByteArrayFromFilePath(uploaded_files[i]))
        }
        client.GetFebStats({boxscores: data}, function (err, response) {
            console.log('Response:', response);
            console.log('Err:', err);
            res.writeHead(200, {'Content-Type': 'application/force-download','Content-disposition':'attachment; filename=a.xlsx'});
            res.end(response['sheet']);


        });

 });



/*



function getByteArrayFromFile(file) {
    let fileData = file.toString('hex');
    let result = [];
    for (var i = 0; i < fileData.length; i += 2)
        result.push('0x' + fileData[i] + '' + fileData[i + 1]);
    return result;
}


app.post('/analyze_stats', (req, res) => {
    console.log('in /analyze_stats!');
    console.log(req.body.boxscores_input);
    var uploaded_files = [];
    const files = req.body.boxscores_input;
    console.log(files);
    Object.keys(files).forEach(i => {
        const file = files[i];
        const reader = new window.FileReader();

        reader.onload = (e) => {
            uploaded_files.push(reader.result);
        };
        reader.readAsBinaryString(file);
    });

    console.log(uploaded_files);
    data = [getByteArray(uploaded_files[0]),
        getByteArray(uploaded_files[1])];

    client.GetFebStats({boxscores: data}, function (err, response) {
        console.log('Response:', response);
        console.log('Err:', err);
    });
    res.end()

});

app.post('/submit-form', (req, res) => {
    const username = req.body.username;
    console.log(username);
    res.end()
});
*/

app.listen(8081, () => {
    console.log('Express server listening on port 8081');
});
