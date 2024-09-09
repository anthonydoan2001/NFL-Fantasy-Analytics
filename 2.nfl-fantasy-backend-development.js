# Section 2: Backend Development

## 2.1 Setting up Node.js server with Express

First, let's set up our Node.js project and install necessary dependencies:

```bash
mkdir nfl-fantasy-backend
cd nfl-fantasy-backend
npm init -y
npm install express mysql2 sequelize dotenv cors
npm install --save-dev nodemon
```

Now, let's create our main server file `server.js`:

```javascript
const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// Routes will be added here

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
```

## 2.2 Database Setup

Create a `.env` file in the root directory:

```
DB_NAME=nfl_fantasy
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

Now, let's set up our database connection and models using Sequelize. Create a `models` directory and add `index.js`:

```javascript
const { Sequelize } = require('sequelize');
const dotenv = require('dotenv');

dotenv.config();

const sequelize = new Sequelize(process.env.DB_NAME, process.env.DB_USER, process.env.DB_PASSWORD, {
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  dialect: 'mysql',
});

const db = {};

db.Sequelize = Sequelize;
db.sequelize = sequelize;

// Import models
db.Player = require('./player.model')(sequelize, Sequelize);
db.User = require('./user.model')(sequelize, Sequelize);
db.Team = require('./team.model')(sequelize, Sequelize);
db.League = require('./league.model')(sequelize, Sequelize);

// Define associations
db.User.hasMany(db.Team);
db.Team.belongsTo(db.User);

db.League.hasMany(db.Team);
db.Team.belongsTo(db.League);

db.Team.belongsToMany(db.Player, { through: 'TeamPlayers' });
db.Player.belongsToMany(db.Team, { through: 'TeamPlayers' });

module.exports = db;
```

Now, let's create our models. Here's an example for the `Player` model (`models/player.model.js`):

```javascript
module.exports = (sequelize, DataTypes) => {
  const Player = sequelize.define('Player', {
    name: {
      type: DataTypes.STRING,
      allowNull: false,
    },
    position: {
      type: DataTypes.ENUM('QB', 'RB', 'WR', 'TE', 'K', 'DEF'),
      allowNull: false,
    },
    team: {
      type: DataTypes.STRING,
      allowNull: false,
    },
    fantasyPoints: {
      type: DataTypes.FLOAT,
      allowNull: false,
    },
    projectedPoints: {
      type: DataTypes.FLOAT,
      allowNull: false,
    },
  });

  return Player;
};
```

Create similar model files for `User`, `Team`, and `League`.

## 2.3 API Endpoints

Let's create some basic API endpoints. First, create a `routes` directory and add `player.routes.js`:

```javascript
const express = require('express');
const router = express.Router();
const db = require('../models');
const Player = db.Player;

// Get all players
router.get('/', async (req, res) => {
  try {
    const players = await Player.findAll();
    res.json(players);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

// Get a specific player
router.get('/:id', async (req, res) => {
  try {
    const player = await Player.findByPk(req.params.id);
    if (player) {
      res.json(player);
    } else {
      res.status(404).json({ message: 'Player not found' });
    }
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

// Add more routes for creating, updating, and deleting players

module.exports = router;
```

Create similar route files for `user.routes.js`, `team.routes.js`, and `league.routes.js`.

Now, let's update our `server.js` to include these routes:

```javascript
// ... (previous code)

const playerRoutes = require('./routes/player.routes');
const userRoutes = require('./routes/user.routes');
const teamRoutes = require('./routes/team.routes');
const leagueRoutes = require('./routes/league.routes');

app.use('/api/players', playerRoutes);
app.use('/api/users', userRoutes);
app.use('/api/teams', teamRoutes);
app.use('/api/leagues', leagueRoutes);

// ... (rest of the code)
```

## 2.4 Database Initialization

Add this to your `server.js` to initialize the database:

```javascript
const db = require('./models');

db.sequelize.sync({ force: true }).then(() => {
  console.log("Drop and re-sync db.");
});
```

Note: Using `force: true` will drop and recreate all tables. Use this carefully, especially in a production environment.

