const mongoose = require('mongoose');
const Schema = mongoose.Schema;

var userSchema = new Schema({
	id: String,
	access_token: String,
	firstName: String,
	lastName: String,
	email: String,
	learning_engine: { type: String, default: '' },
	player_games: [Schema.Types.Mixed],
	trainAI_games: [Schema.Types.Mixed]
});

var User = mongoose.model('User', userSchema);
module.exports = User;
