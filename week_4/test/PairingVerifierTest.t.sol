// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.25;

import {Test, console} from "forge-std/Test.sol";
import {PairingVerifier} from "../src/PairingVerifier.sol";

contract PairingVerifierTest is Test {
    PairingVerifier verifier;

    function setUp() public {
        verifier = new PairingVerifier();
    }

    function testVerifier() public view {
        PairingVerifier.G1Point memory A1 = PairingVerifier.G1Point({
            x: 3932705576657793550893430333273221375907985235130430286685735064194643946083,
            y: 18813763293032256545937756946359266117037834559191913266454084342712532869153
        });
        PairingVerifier.G2Point memory B2 = PairingVerifier.G2Point({
            x1: 8472151341754925747860535367990505955708751825377817860727104273184244800723,
            x2: 15624790064206502667756020446826209080711344272800176518784649088946231692936,
            y1: 1196137947243150610106053819405501111182787323156221967342356892090037828244,
            y2: 19488077321171448217727198730828487286865984357780136663388739985720647978898
        });
        PairingVerifier.G1Point memory C1 = PairingVerifier.G1Point({
            x: 3010198690406615200373504922352659861758983907867017329644089018310584441462,
            y: 4027184618003122424972590350825261965929648733675738730716654005365300998076
        });
        uint256 x1 = 10;
        uint256 x2 = 2;
        uint256 x3 = 8;

        assertTrue(verifier.pairing(A1, B2, C1, x1, x2, x3));
    }
}
