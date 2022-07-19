The file brownie-config allows you to run swap.py file in:
1. Local net: mainnet-fork-dev 
2. Testnet: kovan

Using SushiSwap Weth-Dai Liquidity Pool, when running the file the result will be:
1. Swap Weht for Dai
2. Re-Swap Dai for Weth

You will be ask to input the amount for both transactions.

The tasks in sequance are:
1. Get Weth: this runs only if in local
2. Approve amount of Weht to be swapped - your input
3. Swap Weht for Dai
4. Approve amount of Dai to be swapped - your input
5. Swap Dai for Weht

You can call these functions separately:
1. swap
2. get_weth

Swap function calls the following function from the router interface IUniswapV2Router02.sol:
- swapExactTokensForTokens(        
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline)

Most of the code is based on Patrick Collins tutorials, specifically;
- https://www.youtube.com/watch?v=TmNGAvI-RUA&list=PL4Rj_WH6yLgVP_P-1Jxzu_EfmwXNleM0a