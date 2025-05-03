// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.25;

import {Test, console} from "forge-std/Test.sol";

contract PairingVerifier {
    struct G1Point {
        uint256 x;
        uint256 y;
    }

    struct G2Point {
        uint256 x1;
        uint256 x2;
        uint256 y1;
        uint256 y2;
    }

    address public constant ADD_POINTS = address(6);
    address public constant MUL_SCALAR = address(7);
    address public constant PAIRING = address(8);

    // curve order (bn128)
    uint256 n =
        21888242871839275222246405745257275088696311157297823662689037894645226208583;

    G1Point G1 = G1Point({x: 1, y: 2});
    G1Point alfa1 =
        G1Point({
            x: 3932705576657793550893430333273221375907985235130430286685735064194643946083,
            y: 18813763293032256545937756946359266117037834559191913266454084342712532869153
        });
    G2Point beta2 =
        G2Point({
            x1: 2725019753478801796453339367788033689375851816420509565303521482350756874229,
            x2: 7273165102799931111715871471550377909735733521218303035754523677688038059653,
            y1: 2512659008974376214222774206987427162027254181373325676825515531566330959255,
            y2: 957874124722006818841961785324909313781880061366718538693995380805373202866
        });
    G2Point gamma2 =
        G2Point({
            x1: 2725019753478801796453339367788033689375851816420509565303521482350756874229,
            x2: 7273165102799931111715871471550377909735733521218303035754523677688038059653,
            y1: 2512659008974376214222774206987427162027254181373325676825515531566330959255,
            y2: 957874124722006818841961785324909313781880061366718538693995380805373202866
        });

    G2Point delta2 =
        G2Point({
            x1: 10857046999023057135944570762232829481370756359578518086990519993285655852781,
            x2: 11559732032986387107991004021392285783925812861821192530917403151452391805634,
            y1: 8495653923123431417604973247489272438418190587263600148770280649306958101930,
            y2: 4082367875863433681332203403145435568316851327593401208105741076214120093531
        });

    function neg(G1Point memory point) public view returns (G1Point memory) {
        if (point.x == 0 && point.y == 0) {
            return G1Point(0, 0);
        } else {
            return G1Point({x: point.x, y: n - (point.y % n)});
        }
    }

    function addPoints(
        G1Point memory point1,
        G1Point memory point2
    ) public view returns (G1Point memory) {
        bytes memory data = abi.encode(point1.x, point1.y, point2.x, point2.y);

        (bool success, bytes memory returned) = ADD_POINTS.staticcall(data);
        require(success, "addition failed");

        return abi.decode(returned, (G1Point));
    }

    function mulScalar(
        G1Point memory point,
        uint256 scalar
    ) public view returns (G1Point memory) {
        bytes memory data = abi.encode(point.x, point.y, scalar);

        (bool success, bytes memory returned) = MUL_SCALAR.staticcall(data);
        require(success, "multiplication failed");

        return abi.decode(returned, (G1Point));
    }

    function pairing(
        G1Point memory a1,
        G2Point memory b2,
        G1Point memory c1,
        uint256 x1,
        uint256 x2,
        uint256 x3
    ) public view returns (bool) {
        G1Point memory X1 = mulScalar(G1, x1 + x2 + x3);
        G1Point[4] memory p1 = [neg(a1), alfa1, X1, c1];
        G2Point[4] memory p2 = [b2, beta2, gamma2, delta2];

        uint256 inputSize = 24;
        uint256[] memory input = new uint256[](inputSize);

        for (uint256 i = 0; i < 4; i++) {
            uint256 j = i * 6;
            input[j + 0] = p1[i].x;
            input[j + 1] = p1[i].y;
            input[j + 2] = p2[i].x2;
            input[j + 3] = p2[i].x1;
            input[j + 4] = p2[i].y2;
            input[j + 5] = p2[i].y1;
        }

        (bool success, bytes memory returned) = PAIRING.staticcall(
            abi.encodePacked(input)
        );
        require(success, "pairing failed");

        return abi.decode(returned, (bool));
    }
}
