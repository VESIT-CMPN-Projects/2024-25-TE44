require("dotenv").config({ path: "../environ.env" });

const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const bcrypt=require("bcryptjs");
const User=require("./models/User");

const app = express();
app.use(cors());
app.use(express.json());
app.use("/uploads", express.static("uploads"));

const PORT = process.env.PORT || 5000;

// Connect to MongoDB
mongoose.connect(process.env.MONGO_URI).then(() => console.log("MongoDB Connected"))
  .catch(err => console.log(err));

// Routes
const uploadRoutes = require("./routes/upload");
app.use("/api/upload", uploadRoutes);
app.post("/register",async(req,res)=>{
  try{
    const {username,password}=req.body;
    const existingUser=await User.findOne({ username });
    if(existingUser){
      return res.status(400).json({ message: "Username already taken" });
    }
    const hashedPassword=await bcrypt.hash(password,10);
    const newUser= new User({ username, password: hashedPassword });
    await newUser.save();
    res.json({ message: "User Registered successfully"});
  }
  
   catch(err)
   {
     res.status(500).json({ message: "Server error" });
  }
});
app.post("/login",async(req,res)=>{
  try{
  const{username,password}=req.body;
  const user=await User.findOne({ username });
  if(!user){
    return res.status(400).json({ message: "User not found" });
  }
  const isMatch=await bcrypt.compare(password,user.password);
  if(!isMatch)
  {
    return res.status(400).json({ message: "Invalid Credentials" });
  }
  res.json({message: "Success"});
}
catch(err){
  res.status(500).json({ message: "Server Error" });
}
});
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
