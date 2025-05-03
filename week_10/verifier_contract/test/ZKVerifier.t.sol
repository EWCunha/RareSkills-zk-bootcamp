// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";
import {ZKVerifier} from "../src/ZKVerifier.sol";

contract CounterTest is Test {
    ZKVerifier public zkVerifier;

    ZKVerifier.G1Point public A1 =
        ZKVerifier.G1Point({
            x: 16891539659470176737911824658181641627645483647167181886898897866533309810236,
            y: 5468902215564682685860038818061453630377801118095748128186407857030479111922
        });

    ZKVerifier.G2Point public B2 =
        ZKVerifier.G2Point({
            x1: 14672215183750697287151399449764699529555724485943517718323062398025624747480,
            x2: 1849235896074215913371507361462789587806491992677627971524344487561375007892,
            y1: 10104589629049301980928576093326449748925963455922691156623718000730187508007,
            y2: 17689133748408580688119979480322085240152595192285614083466111807506581381340
        });

    ZKVerifier.G1Point public C1 =
        ZKVerifier.G1Point({
            x: 17488131258434106912737600577830142040606459427287500157834940835734164827267,
            y: 7429957725847393516822829429738296822895837891237905010518651412634632428795
        });

    uint256[3] public inputs = [1, 1, 2];

    // uint256[3] public inputs = [2, 1, 1];

    function setUp() public {
        zkVerifier = new ZKVerifier();
    }

    function test_Proof() public view {
        bool proved = zkVerifier.verify(inputs, A1, B2, C1);

        assertTrue(proved);
    }
}
