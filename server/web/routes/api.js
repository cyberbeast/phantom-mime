const router = require('express').Router();
const passport = require('passport');
const FacebookStrategy = require('passport-facebook').Strategy;
const mongoose = require('mongoose');
var User = require('../models/user');
const Config = require('../config');
const path = require('path');
const fs = require('fs');

mongoose.connect('mongodb://mongodb/', {
	useMongoClient: true
});

router.get('/', function(req, res, next) {
	console.log('API');
});

passport.use(
	'facebook',
	new FacebookStrategy(
		{
			clientID: Config.fb.appID,
			clientSecret: Config.fb.appSecret,
			callbackURL: Config.fb.callbackUrl,
			profileFields: ['id', 'displayName', 'emails', 'name']
		},

		// facebook will send back the tokens and profile
		function(access_token, refresh_token, profile, done) {
			// asynchronous
			// console.log(profile);
			process.nextTick(function() {
				// find the user in the database based on their facebook id
				User.findOne({ id: profile.id }, function(err, user) {
					// if there is an error, stop everything and return that
					// ie an error connecting to the database
					if (err) return done(err);

					// if the user is found, then log them in
					if (user) {
						return done(null, user); // user found, return that user
					} else {
						// if there is no user found with that facebook id, create them
						var newUser = new User();

						// set all of the facebook information in our user model
						newUser.id = profile.id; // set the users facebook id
						newUser.access_token = access_token; // we will save the token that facebook provides to the user
						newUser.firstName = profile.name.givenName;
						newUser.lastName = profile.name.familyName; // look at the passport user profile to see how names are returned
						newUser.email = profile.emails[0].value; // facebook can return multiple emails so we'll take the first

						// save our user to the database
						newUser.save(function(err) {
							if (err) throw err;

							// if successful, return the new user
							return done(null, newUser);
						});
					}
				});
			});
		}
	)
);

router.use(passport.initialize());
router.use(passport.session());

// route for facebook authentication and login
// different scopes while logging in
router.get('/login/facebook', passport.authenticate('facebook', { scope: 'email' }));

// handle the callback after facebook has authenticated the user
router.get(
	'/login/facebook/callback',
	passport.authenticate('facebook', {
		failureRedirect: '/api'
	}),
	function(req, res) {
		// console.log(JSON.stringify(req.user));
		console.log('FB called this URL...');
		// console.log(JSON.stringify(req.sessionID));
		res.redirect('/api/dashboard');
	}
);

router.get('/dashboard', function(req, res) {
	if (req.isUnauthenticated()) {
		res.redirect('/../client/index.html');
	}
	req.session.fbid = req.user.id;
	req.session.email = req.user.email;
	res.sendFile(path.join(__dirname + '/../client/dashboard.html'));
});

router.get('/game', function(req, res) {
	if (req.isAuthenticated()) {
		req.session.fbid = req.user.id;
		req.session.email = req.user.email;
		req.session.gSession = req.query.gameID;
		if (req.query.mode === 'trainAI') {
			req.session.gameMode = 'trainAI';
		} else {
			req.session.gameMode = 'PvP';
			req.session.p2 = req.query.player2;
		}
		req.session.p1 = req.query.player1;
		// check for existence player2
		res.sendFile(path.join(__dirname + '/../client/game.html'));
	} else {
		res.send('ERROR');
	}
});

passport.serializeUser(function(user, done) {
	done(null, user.id);
});

passport.deserializeUser(function(id, done) {
	User.findOne({ id: String(id) }, function(err, user) {
		// console.log(user);
		done(err, user);
	});
});

module.exports = router;
