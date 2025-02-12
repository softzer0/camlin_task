#!/bin/bash
set -e

# Wait for MongoDB to be ready
echo "Waiting for MongoDB..."
while ! mongosh --eval "db.adminCommand('ping')" mongodb:27017/wallet_app &>/dev/null; do
    sleep 1
done
echo "MongoDB is ready!"

# Wait for Redis to be ready
echo "Waiting for Redis..."
while ! redis-cli -h redis ping &>/dev/null; do
    sleep 1
done
echo "Redis is ready!"

# Initialize MongoDB indexes
echo "Creating MongoDB indexes..."
mongosh mongodb:27017/wallet_app --eval '
    db.wallets.createIndex({"user_id": 1}, {unique: true});
    db.users.createIndex({"email": 1}, {unique: true});
'
echo "Indexes created!"
