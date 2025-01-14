const express = require('express');
const SerialPort = require('serialport');
const ReadlineParser = require('@serialport/parser-readline');
const cors = require('cors'); // CORS modülü

const app = express();
const portNumber = 3000;

let latestData = ''; // Gelen son veriyi saklamak için

// CORS ayarları
app.use(cors()); // Tüm kaynaklara izin ver

// Seri port yapılandırması
//const serialPort = new SerialPort('/dev/ttyS1', { baudRate: 9600 });
const serialPort = new SerialPort('COM6', { baudRate: 9600 });
//const serialPort = new SerialPort('/dev/ttyUSB0', { baudRate: 9600 });
const parser = serialPort.pipe(new ReadlineParser({ delimiter: '\r\n' }));

// Seri porttan veri alındığında
parser.on('data', (data) => {
    console.log(`Received data: ${data}`);
    latestData = data; // Son veriyi sakla
});

// Seri port hata yönetimi
serialPort.on('error', (err) => {
    console.error(`Serial Port Error: ${err.message}`);
});

// Seri port bağlantısı kontrolü
serialPort.on('open', () => {
    console.log('Serial Port Opened');
});

// HTTP endpoint
app.get('/data', (req, res) => {
    res.setHeader('Content-Type', 'application/json'); // Yanıt türünü ayarla
    res.json({ data: latestData || 'No data received yet' }); // JSON formatında veri döndür
});

// Sunucuyu başlat
app.listen(portNumber, () => {
    console.log(`Server is running at http://localhost:${portNumber}`);
});
