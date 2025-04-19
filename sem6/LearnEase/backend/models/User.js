const mongoose = require("mongoose");

const UserSchema = new mongoose.Schema({
  username: { type: String, required: true, unique: true },
  password: { type: String, required: true }, 
  class: { type: String },
  subjects: [{ type:String }]
});

module.exports = mongoose.model("User", UserSchema);
