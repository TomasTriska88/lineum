<script lang="ts">
    import ShowcaseTemplate from "./ShowcaseTemplate.svelte";
</script>

<ShowcaseTemplate
    badge="3 / 5 API SUITE"
    title="Web3 Oracle API"
    description="Specialized formatting of the exact Zeta entropy designed for zero-knowledge proofs (ZK-Rollups) and smart contracts requiring a mathematically provable 'trusted setup'."
    traditionalTitle="Standard VRF Solutions"
    traditionalDesc="Chainlink VRF and similar solutions rely on decentralized nodes and cryptographic verification but do not provide physical/topological guarantees."
    lineumTitle="Topological ZK Trusted Seed"
    lineumDesc="Provides a seed formatted directly for elliptic curve generation, backed by mathematical proofs of the topological collapse."
    language="solidity"
    codeSnippet={`// Example Contract Integration
import "@lineum/contracts/LineumOracle.sol";

contract TrustedSetup is LineumConsumer {
    bytes32 public zkSeed;
    
    function requestSetupSeed() external {
        requestLineumZetaEntropy(
            /* callback gas limit */ 100000,
            /* confirmations */ 3
        );
    }
    
    function fulfillZetaEntropy(bytes32 entropy) internal override {
        zkSeed = entropy;
    }
}`}
>
    <!-- Visual -->
    <div
        slot="visual"
        class="w-full flex items-center justify-center p-8 bg-slate-950/80 rounded-3xl border border-sky-500/20 shadow-[0_0_40px_rgba(56,189,248,0.1)] overflow-hidden h-[400px] relative"
    >
        <div
            class="absolute inset-0 flex items-center justify-center opacity-50"
        >
            <svg
                class="w-32 h-32 text-sky-500/50"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1"
                ><path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"
                ></path></svg
            >
            <div
                class="absolute text-sky-400 font-mono text-sm tracking-widest font-bold mt-32"
            >
                ZK-PROOF TRUSTED SEED GENERATION
            </div>
        </div>
    </div>

    <!-- Proof -->
    <div
        slot="proof"
        class="w-full bg-slate-950 border border-slate-800 rounded-2xl p-6 flex flex-col justify-center gap-4 text-xs font-mono text-slate-400"
    >
        <div class="flex justify-between border-b border-slate-800 pb-2">
            <span>TARGET AUDIENCE</span>
            <span class="text-white">Ethereum L2, Crypto Engineers</span>
        </div>
        <div class="flex justify-between">
            <span>OUTPUT FORMAT</span>
            <span class="text-emerald-400">Elliptic Curve Base Points</span>
        </div>
    </div>
</ShowcaseTemplate>
