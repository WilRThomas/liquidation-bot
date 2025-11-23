## Daily Startup Commands

### 1. Start Anvil
anvil --fork-url $RPC_URL --fork-block-number 19900000

### 2. In a second terminal, go to the project root
cd "/Users/williamthomas/Liquidation Bot Parent/liquidation-bot"
source venv/bin/activate

### 3. Run tools
python3 -m src.tools.seed_test_account


Directory Structure:

src/
The actual bot code
Where the architecture actually lives

src/__init__.py
Marks the folder as a python package
Ignore, pure environmental metadata

src/check_chain_and_balance.py
Utility scrip from early setup stage
Checks RPC connectivity, ETH balance, WETH balance, Fork network correctness

src/config.py
Configuration loader
Load .env variables, load static contract addresses, provide constants

src/core/
High Level bot logic
Where you compute liquidation thresholds, repay amount, seize amount, gas cost, slippage, expected profit

src/core/executor.py
Handles sending transactions
Signing liquidation transactions, managing nonces, applying gas strategies, retrying failed submissions, writing receipts to logs

src/core/state_fetcher.py
Module reads DeFi protocol state
Reads user health factor, collateral value, borrow value, oracle prices, reserve configuration

src/core/tx_builder.py
Constructs the actual liquidation transaction
Prepares calldata, assembles parameters for the liquidation function, simulates the call using eth_call, prepares write-ready transaction dictionaries

src/data/
Folder for JSON files, static metadata, cached protocol data, etc

src/main.py
Orchestrator or entrypoint
Responsible for starting the bot, starting listeners or polling loops, runs state fetcher > calculator > tx builder > executor, manage periodic timers

src/monitoring/
Logging and visualisation layer

src/monitoring/dashboard.py
If you make a CLI dashboard or logs screen, it goes here
Shows number of accounts scanned, number of liquidation condidates, profitable opportunities found, network stats

src/monitoring/logger.py
Centralised logging
Handles structured logs, timestamps, formatting, error loggin, writing to file

src/sdk/
Structured directory of tools, functions and utilities

src/sdk/init.py
Exports shortcuts

src/sdk/abi_loader.py
Loads ABIs from ABI folder and returns ABI dicts, contract objects

src/sdk/addresses.py
Utilities
Convert to checksum, validate Ethereum addresses, hold canonical protocol addresses

src/sdk/clients.py
Web3 client factory
Central place for creating Web3 connections, adding RPC middleware, configuring retries, controlling batch providers

sdk/retry.py
Helper for flaky RPC operations, intermittent Anvil failures, long running polling loops

src/tools/
Standalone utility scripts to manually

src/tools/seed_test_account
Used to mint WETH, seed borrower + liquidator accounts, check balances in local fork