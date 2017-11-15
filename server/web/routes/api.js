const server = require('../index.js').server;
const express = require('express');
const redis = require('redis');
const router = express.Router();

router.get('/', function(req, res, next) {
	console.log('ok');
});

module.exports = router;
