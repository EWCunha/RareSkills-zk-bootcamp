// SPDX-License-Identifier: MIT
pragma solidity 0.8.25;

import {Test, console} from "forge-std/Test.sol";

contract ECPoints is Test {
    struct ECPoint {
        uint256 x;
        uint256 y;
    }

    // curve order (bn128)
    uint256 n =
        21888242871839275222246405745257275088548364400416034343698204186575808495617;
    // Generator point (bn128)
    ECPoint G = ECPoint({x: 1, y: 2});

    function rationalAdd(
        ECPoint calldata A,
        ECPoint calldata B,
        uint256 num,
        uint256 den
    ) public returns (bool verified) {
        ECPoint memory addedPoint = add(A.x, A.y, B.x, B.y);
        uint256 modResult = mulmod(num, modexp(den, n - 2, n), n);
        ECPoint memory resultPoint = mul(G.x, G.y, modResult);

        verified =
            resultPoint.x == addedPoint.x &&
            resultPoint.y == addedPoint.y;
    }

    function matmul(
        uint256[][] calldata matrix,
        uint256 n_, // n x n for the matrix
        ECPoint[] calldata s, // n elements
        uint256[] calldata o // n elements
    ) public view returns (bool verified) {
        for (uint256 r = 0; r < n_; ++r) {
            ECPoint memory result;
            for (uint256 c = 0; c < n_; ++c) {
                ECPoint memory point = mul(s[c].x, s[c].y, matrix[r][c]);
                if (c == 0) {
                    result = point;
                } else {
                    result = add(result.x, result.y, point.x, point.y);
                }
            }
            ECPoint memory oPoint = mul(G.x, G.y, o[r]);
            verified = result.x == oPoint.x && result.y == oPoint.y;
            if (!verified) {
                break;
            }
        }
    }

    function matmul(
        uint256[] calldata matrix,
        uint256 n_, // n x n for the matrix
        ECPoint[] calldata s, // n elements
        uint256[] calldata o // n elements
    ) public view returns (bool verified) {
        uint256 vector_index;
        ECPoint memory result;
        for (uint256 elem = 0; elem < matrix.length; ++elem) {
            vector_index = elem % n_;
            ECPoint memory point = mul(
                s[vector_index].x,
                s[vector_index].y,
                matrix[elem]
            );
            if (vector_index == 0) {
                result = point;
            } else {
                result = add(result.x, result.y, point.x, point.y);
            }
        }
    }

    function modexp(
        uint256 _b,
        uint256 _e,
        uint256 _m
    ) internal returns (uint256 result) {
        assembly {
            // Free memory pointer
            let pointer := mload(0x40)

            // Define length of base, exponent and modulus. 0x20 == 32 bytes
            mstore(pointer, 0x20)
            mstore(add(pointer, 0x20), 0x20)
            mstore(add(pointer, 0x40), 0x20)

            // Define variables base, exponent and modulus
            mstore(add(pointer, 0x60), _b)
            mstore(add(pointer, 0x80), _e)
            mstore(add(pointer, 0xa0), _m)

            // Store the result
            let value := mload(0xc0)

            // Call the precompiled contract 0x05 = bigModExp
            if iszero(call(not(0), 0x05, 0, pointer, 0xc0, value, 0x20)) {
                revert(0, 0)
            }

            result := mload(value)
        }
    }

    function add(
        uint256 x1,
        uint256 y1,
        uint256 x2,
        uint256 y2
    ) internal view returns (ECPoint memory) {
        (bool ok, bytes memory returnedValue) = address(6).staticcall(
            abi.encode(x1, y1, x2, y2)
        );

        require(ok, "Add failed");
        (uint256 x, uint256 y) = abi.decode(returnedValue, (uint256, uint256));

        return ECPoint({x: x, y: y});
    }

    function mul(
        uint256 x,
        uint256 y,
        uint256 scalar
    ) internal view returns (ECPoint memory) {
        (bool ok, bytes memory returnedValue) = address(7).staticcall(
            abi.encode(x, y, scalar)
        );

        require(ok, "Mul failed");
        (uint256 x_, uint256 y_) = abi.decode(
            returnedValue,
            (uint256, uint256)
        );

        return ECPoint({x: x_, y: y_});
    }
}
