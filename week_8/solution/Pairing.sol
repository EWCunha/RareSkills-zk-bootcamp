// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Pairing {
    struct ECPoint {
        uint256 x;
        uint256 y;
    }

    struct ECPoint2 {
        uint256 x1;
        uint256 x2;
        uint256 y1;
        uint256 y2;
    }

    uint256 public constant field_modulus =
        21888242871839275222246405745257275088696311157297823662689037894645226208583;

    function pairing(
        uint256[12] memory points
    ) public view returns (uint256 success) {
        (bool ok, bytes memory result) = address(8).staticcall(
            abi.encode(points)
        );
        require(ok, "pairing failed");
        success = abi.decode(result, (uint256));
    }

    function verifier() public view returns (bool result) {
        ECPoint memory A1 = ECPoint(
            2020083486884613231143009227578316708530491376242328436263280512260631043615,
            16791848345070161134920543037265406555643776923125235542125727131344132153999
        );

        ECPoint2 memory B2 = ECPoint2(
            5627264143025035642251472381094424923351592387684025510767403988802941749823,
            15538867084289426179120166236963072678642825086349504736967553090361807396652,
            10173919014584226836272436242723050027266785317887814226867273521779628305713,
            15672310064662809767961392466364363221768415284607199412803774298944312277690
        );

        ECPoint memory C1 = ECPoint(
            6936152028451513581263490767360917185829903520620035662240146739651938619655,
            18054778541685754303699851694596109487234259244724190225698242508006932949547
        );

        ECPoint2 memory G2 = ECPoint2(
            10857046999023057135944570762232829481370756359578518086990519993285655852781,
            11559732032986387107991004021392285783925812861821192530917403151452391805634,
            8495653923123431417604973247489272438418190587263600148770280649306958101930,
            4082367875863433681332203403145435568316851327593401208105741076214120093531
        );

        uint256 negative_A1_x = A1.x;
        uint256 negative_A1_y = field_modulus - A1.y;

        uint256[12] memory points = [
            negative_A1_x,
            negative_A1_y,
            B2.x2,
            B2.x1,
            B2.y2,
            B2.y1,
            C1.x,
            C1.y,
            G2.x2,
            G2.x1,
            G2.y2,
            G2.y1
        ];

        uint256 success = pairing(points);
        result = success == 1;
    }
}
